package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"maps"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"time"

	testutil "github.com/VictoriaMetrics/VictoriaMetrics/app/victoria-metrics/test"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmalert/config"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmalert/datasource"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmalert/notifier"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmalert/remotewrite"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmalert/rule"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vminsert"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vminsert/promremotewrite"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmselect"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmselect/prometheus"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmselect/promql"
	"github.com/VictoriaMetrics/VictoriaMetrics/app/vmstorage"
	"github.com/VictoriaMetrics/VictoriaMetrics/lib/fs"
	"github.com/VictoriaMetrics/VictoriaMetrics/lib/httpserver"
	"github.com/VictoriaMetrics/VictoriaMetrics/lib/logger"
	"github.com/VictoriaMetrics/VictoriaMetrics/lib/promutil"
	"github.com/VictoriaMetrics/metrics"
)

var (
	storagePath    string
	httpListenAddr string
	// insert series from 1970-01-01T00:00:00
	testStartTime          = time.Unix(0, 0).UTC()
	testLogLevel           = "ERROR"
	disableAlertgroupLabel bool
)

const (
	testStoragePath = "vmalert-unittest"
)

func main() {
	var server *httptest.Server
	server, httpListenAddr = startVictoriaMetricsAPI()
	defer server.Close()

	tc, err := waitOnTestCase()
	if err != nil {
		logger.Fatalf("failed to read test case from stdin: %v", err)
	}

	runTestInVictoriaMetrics(tc)
}

func waitOnTestCase() (TestCase, error) {
	var tc TestCase
	err := json.NewDecoder(os.Stdin).Decode(&tc)
	return tc, err
}

func startVictoriaMetricsAPI() (*httptest.Server, string) {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/prometheus/api/v1/query":
			if err := prometheus.QueryHandler(nil, time.Now(), w, r); err != nil {
				httpserver.Errorf(w, r, "%s", err)
			}
		case "/prometheus/api/v1/write", "/api/v1/write":
			if err := promremotewrite.InsertHandler(r); err != nil {
				httpserver.Errorf(w, r, "%s", err)
			}
		default:
		}
	})
	server := httptest.NewServer(handler)
	listenAddr := strings.Split(server.URL, ":")[2]
	return server, listenAddr
}

func runTestInVictoriaMetrics(testCase TestCase) {
	tmpFolder, err := os.MkdirTemp(os.TempDir(), testStoragePath)
	if err != nil {
		logger.Fatalf("failed to create tmp dir for tests: %v", err)
	}
	storagePath = tmpFolder
	processFlags()
	vminsert.Init()
	vmselect.Init()
	// storagePath will be created again when closing vmselect, so remove it again.
	defer fs.MustRemoveDir(storagePath)
	defer vminsert.Stop()
	defer vmselect.Stop()

	_, err = notifier.Init(nil, make(map[string]string), "extern")
	if err != nil {
		logger.Fatalf("failed to init notifier: %v", err)
	}

	runTest(testCase)

}

type SerializableDuration time.Duration

func (s *SerializableDuration) UnmarshalJSON(data []byte) error {
	var milliseconds int64
	if err := json.Unmarshal(data, &milliseconds); err != nil {
		return err
	}

	*s = SerializableDuration(time.Duration(milliseconds) * time.Millisecond)

	return nil
}

func (s SerializableDuration) Unwrap() time.Duration {
	return time.Duration(s)
}

type TestRuleConfig struct {
	Alert         string                `json:"alert,omitempty"`
	Expr          string                `json:"expr"`
	For           *SerializableDuration `json:"for,omitempty"`
	KeepFiringFor *SerializableDuration `json:"keep_firing_for,omitempty"`
	Labels        map[string]string     `json:"labels,omitempty"`
	Annotations   map[string]string     `json:"annotations,omitempty"`
}

func (t TestRuleConfig) AsPlainConfig() config.Rule {
	r := config.Rule{
		Alert:       t.Alert,
		Expr:        t.Expr,
		Labels:      t.Labels,
		Annotations: t.Annotations,
	}

	if t.For != nil {
		r.For = promutil.NewDuration(t.For.Unwrap())
	}
	if t.KeepFiringFor != nil {
		r.KeepFiringFor = promutil.NewDuration(t.KeepFiringFor.Unwrap())
	}

	// normally this is done during yaml unmarshal
	r.ID = config.HashRule(r)

	return r
}

type TestCase struct {
	Rule       *TestRuleConfig `json:"rule"`
	Expression string          `json:"expression"`

	InitialSeries []TimeSeries `json:"initial_series"`

	Interval   SerializableDuration `json:"interval"`
	StartAfter SerializableDuration `json:"start_after"`
	Steps      int                  `json:"steps"`
}

type TestRunner interface {
	Sample(ctx context.Context, t time.Time) error
}

type OutputAlert struct {
	Labels      map[string]string   `json:"labels"`
	Annotations map[string]string   `json:"annotations"`
	State       notifier.AlertState `json:"state"`
	ActiveAt    time.Time           `json:"active_at"`
	ResolvedAt  time.Time           `json:"resolved_at"`
	Value       float64             `json:"value"`
	At          time.Time           `json:"at"`
}

type AlertTestRunner struct {
	Alerts [][]OutputAlert `json:"alerts"`

	group        *rule.Group
	alertingRule *rule.AlertingRule

	rw *remotewrite.DebugClient
}

func NewAlertTestRunner(
	q datasource.QuerierBuilder,
	rw *remotewrite.DebugClient,
	ruleConfig config.Rule,
	interval time.Duration,
) *AlertTestRunner {
	group := rule.NewGroup(config.Group{}, q, interval, make(map[string]string))
	return &AlertTestRunner{
		alertingRule: rule.NewAlertingRule(q, group, ruleConfig),
		group:        group,
		rw:           rw,
	}
}

func (a *AlertTestRunner) Sample(ctx context.Context, t time.Time) error {
	errs := a.group.ExecOnce(ctx, func() []notifier.Notifier { return []notifier.Notifier{} }, a.rw, t)

	var mergedErr error
	for e := range errs {
		mergedErr = errors.Join(mergedErr, e)
	}
	if mergedErr != nil {
		return mergedErr
	}

	samples := []OutputAlert{}
	for _, alert := range a.alertingRule.GetAlerts() {
		samples = append(samples, OutputAlert{
			Labels:      alert.Labels,
			Annotations: alert.Annotations,
			State:       alert.State,
			ActiveAt:    alert.ActiveAt,
			ResolvedAt:  alert.ResolvedAt,
			Value:       alert.Value,
			At:          t,
		})
	}

	a.Alerts = append(a.Alerts, samples)
	return nil
}

type Sample struct {
	Value     float64   `json:"value"`
	Timestamp time.Time `json:"timestamp"`
}

type TimeSeries struct {
	Labels  map[string]string `json:"labels"`
	Samples []Sample          `json:"samples"`
}

func (t TimeSeries) ToTestUtil() testutil.TimeSeries {
	res := testutil.TimeSeries{}
	for name, value := range t.Labels {
		res.Labels = append(res.Labels, testutil.Label{
			Name:  name,
			Value: value,
		})
	}

	for _, s := range t.Samples {
		res.Samples = append(res.Samples, testutil.Sample{
			Value:     s.Value,
			Timestamp: s.Timestamp.UnixMilli(),
		})
	}

	return res
}

type ExpressionTestRunner struct {
	Timeseries []TimeSeries `json:"timeseries"`
	quierer    datasource.Querier
	expression string
}

func NewExpressionTestRunner(q datasource.QuerierBuilder, expression string) *ExpressionTestRunner {
	return &ExpressionTestRunner{
		quierer: q.BuildWithParams(datasource.QuerierParams{
			QueryParams:    url.Values{"nocache": {"1"}, "latency_offset": {"1ms"}},
			DataSourceType: "prometheus"},
		),
		expression: expression,
	}
}

func (e *ExpressionTestRunner) Sample(ctx context.Context, t time.Time) error {
	result, _, err := e.quierer.Query(ctx, e.expression, t)
	if err != nil {
		return err
	}

	for _, timeseries := range result.Data {
		labelMap := map[string]string{}
		for _, lbl := range timeseries.Labels {
			labelMap[lbl.Name] = lbl.Value
		}

		sample := Sample{
			Value:     timeseries.Values[0],
			Timestamp: time.Unix(timeseries.Timestamps[0], 0).UTC(),
		}

		foundIndex := -1
		for i, series := range e.Timeseries {
			if maps.Equal(series.Labels, labelMap) {
				foundIndex = i
			}
		}

		if foundIndex == -1 {
			e.Timeseries = append(e.Timeseries, TimeSeries{
				Labels:  labelMap,
				Samples: []Sample{sample},
			})
		} else {
			e.Timeseries[foundIndex].Samples = append(e.Timeseries[foundIndex].Samples, sample)
		}

	}

	return nil
}

func runTest(c TestCase) {
	setUpVMStorage()
	defer tearDownVMStorage()
	if len(c.InitialSeries) > 0 {
		writeTimeseries(c.InitialSeries)
	}
	q, err := datasource.Init(nil)
	if err != nil {
		logger.Fatalf("failed to init datasource: %v", err)
	}
	rw, err := remotewrite.NewDebugClient()
	if err != nil {
		logger.Fatalf("failed to init remote write: %v", err)
	}

	var testRunner TestRunner
	if c.Rule != nil {

		testRunner = NewAlertTestRunner(q, rw, c.Rule.AsPlainConfig(), c.Interval.Unwrap())
	} else if c.Expression != "" {
		testRunner = NewExpressionTestRunner(q, c.Expression)
	} else {
		logger.Fatalf("invalid test case")
	}

	for s := 0; s < c.Steps; s++ {
		curTime := time.UnixMilli(0).UTC().Add(c.Interval.Unwrap() * time.Duration(s))
		testRunner.Sample(context.Background(), curTime)
	}

	result, err := json.Marshal(testRunner)
	if err != nil {
		logger.Fatalf("failed to serialize result: %v", err)
	}

	fmt.Print(string(result))
}

func writeTimeseries(ts []TimeSeries) {

	r := testutil.WriteRequest{}
	for _, t := range ts {
		r.Timeseries = append(r.Timeseries, t.ToTestUtil())
	}

	data := testutil.Compress(r)
	resp, err := http.Post(fmt.Sprintf("http://127.0.0.1:%s/api/v1/write", httpListenAddr), "", bytes.NewBuffer(data))
	if err != nil {
		logger.Fatalf("failed to send to storage: %v", err)
	}
	resp.Body.Close()
	vmstorage.Storage.DebugFlush()
}

func setUpVMStorage() {
	vmstorage.Init(promql.ResetRollupResultCacheIfNeeded)
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	readyCheckFunc := func() bool {
		resp, err := http.Get(fmt.Sprintf("http://127.0.0.1:%s/health", httpListenAddr))
		if err != nil {
			return false
		}
		_ = resp.Body.Close()
		return resp.StatusCode == 200
	}
checkCheck:
	for {
		select {
		case <-ctx.Done():
			logger.Fatalf("http server can't be ready in 30s")
		default:
			if readyCheckFunc() {
				break checkCheck
			}
			time.Sleep(100 * time.Millisecond)
		}
	}
}

func tearDownVMStorage() {
	vmstorage.Stop()
	metrics.UnregisterAllMetrics()
	fs.MustRemoveDir(storagePath)
}

func processFlags() {
	flag.Parse()
	for _, fv := range []struct {
		flag  string
		value string
	}{
		{flag: "storageDataPath", value: storagePath},
		{flag: "loggerLevel", value: testLogLevel},
		{flag: "search.disableCache", value: "true"},
		// set storage retention time to 100 years, allow to store series from 1970-01-01T00:00:00.
		{flag: "retentionPeriod", value: "100y"},
		{flag: "datasource.url", value: fmt.Sprintf("http://127.0.0.1:%s/prometheus", httpListenAddr)},
		{flag: "remoteWrite.url", value: fmt.Sprintf("http://127.0.0.1:%s", httpListenAddr)},
		{flag: "notifier.blackhole", value: "true"},
	} {
		// panics if flag doesn't exist
		if err := flag.Lookup(fv.flag).Value.Set(fv.value); err != nil {
			logger.Fatalf("unable to set %q with value %q, err: %v", fv.flag, fv.value, err)
		}
	}
}
