package main

import (
	"embed"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/alecthomas/kong"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/hudson-trading/heracles-ql.git/delos/python"
	"github.com/hudson-trading/heracles-ql.git/delos/tui"
)

//go:embed static/*
var devHtml embed.FS

var cli struct {
	Path         *string  `help:"path of python snippet to run"`
	Import       []string `help:"name of module to import for code snippet"`
	Code         *string  `help:"python snippet to run directly"`
	Venv         *string  `help:"path to a python venv for execution"`
	Port         int      `help:"server port" default:"5000"`
	VMUrl        string   `help:"base url of the target VictoriaMetrics instance" required:""`
	BindHostname string   `help:"hostname to print in UI link" default:"localhost" required:""`
}

const helpMessage = `HeraclesQL tool for visualizing queries as you edit them.

Delos allows you to execute a snippet of Python code in your project's venv which produces a
HeraclesQL query. Click on the link that Delos prints to view the generaled MetricsQL
query in the VictoriaMetrics UI. As you edit your project, Delos will re-execute the provided
code snippet to update the query in real time.

There are three modes:
  * interactive mode: Delos will create a temporary file that
      you can edit via your $EDITOR. This is the default behavior if no arguments are
      provided.
  * snippet mode: provide --code to write a Python expression for Delos in the cli.
      use --import to import any modules from your project by name.
  * file mode: provide --path pointing to a Python file which defines VECTOR.

Venv discovery: Delos searches for a venv in the following order:
  1. if --venv is passed, use the venv at the provided path
  2. if VIRTUAL_ENV is set, use the venv it points to
  3. if a venv exists at 'venv', '.venv', or 'env' in the working directory, use it
`

func main() {
	commandCtx := kong.Parse(
		&cli,
		kong.Description(helpMessage),
		kong.UsageOnError(),
	)
	if commandCtx.Error != nil {
		panic(commandCtx.Error)
	}
	pythonCmd, err := findPython()
	if err != nil {
		panic(err)
	}
	fmt.Printf("Found virtual env at '%s'\n", os.Getenv("VIRTUAL_ENV"))
	fmt.Printf("Found python at '%s'\n", pythonCmd)

	executor, err := python.NewExecutor(pythonCmd)
	if err != nil {
		panic(err)
	}

	uiURL := fmt.Sprintf("http://%s:%d/dev", cli.BindHostname, cli.Port)

	executeFn, err := makeExecuteFn(executor, uiURL)
	if err != nil {
		panic(err)
	}

	http.HandleFunc("/dev", func(w http.ResponseWriter, r *http.Request) {
		log.Printf("dev html handler called")
		http.ServeFileFS(w, r, devHtml, "static/index.html")
	})
	http.HandleFunc("/dev/query", fetchQueryHandler(executeFn))
	http.HandleFunc("/{remainingPath...}", proxyVitoriaMetrics(cli.VMUrl))

	fmt.Println(http.ListenAndServe(fmt.Sprintf("0.0.0.0:%d", cli.Port), http.DefaultServeMux))
}

func findPython() (string, error) {
	if cli.Venv != nil {
		// --venv takes priority, even if we're already in a venv
		if err := setupEnvFromVenv(*cli.Venv); err != nil {
			return "", err
		}
	} else if envVar := os.Getenv("VIRTUAL_ENV"); envVar != "" {
		// no need to do anything since we're already in a venv
	} else if localVenv := findVenvInWorkdir(); localVenv != "" {
		if err := setupEnvFromVenv(localVenv); err != nil {
			return "", err
		}
	} else {
		return "", fmt.Errorf("no virtual env found")
	}

	// if we didn't return already, VIRTUAL_ENV is set to something that we think
	// is a python venv
	cmdPath := filepath.Join(os.Getenv("VIRTUAL_ENV"), "bin", "python")

	if _, err := os.Stat(cmdPath); err != nil {
		return "", fmt.Errorf(
			"found a venv, but could not stat '%s' executable: %v",
			cmdPath,
			err,
		)
	}

	return cmdPath, nil
}

func setupEnvFromVenv(venvPath string) error {
	venvAbsPath, err := filepath.Abs(venvPath)
	if err != nil {
		return fmt.Errorf("failed to make VIRTUAL_ENV abs path: %v", err)
	}
	binPath := filepath.Join(venvAbsPath, "bin")
	// set VIRTUAL_ENV and put the venv python at the front of the PATH
	os.Setenv("VIRTUAL_ENV", venvAbsPath)
	os.Setenv("PATH", fmt.Sprintf("%s:%s", binPath, os.Getenv("PATH")))

	return nil
}

func findVenvInWorkdir() string {
	for _, path := range []string{"venv", ".venv", "env"} {
		if stat, err := os.Stat(path); err == nil {
			if stat.IsDir() {
				return path
			}
		}
	}
	return ""
}

func makeExecuteFn(executor *python.Executor, uiURL string) (func() (string, error), error) {
	if cli.Path != nil {
		fmt.Println(uiURL)
		return func() (string, error) {
			return executor.ExecuteFile(*cli.Path)
		}, nil
	}
	if cli.Code != nil {
		fmt.Println(uiURL)
		return func() (string, error) {
			return executor.ExecuteSnippet(python.SnippetExecutionContext{
				Imports: cli.Import,
				Code:    *cli.Code,
			})
		}, nil
	}

	interactiveModeUi, err := tui.NewInteractiveUI(executor, uiURL)
	if err != nil {
		return nil, err
	}
	log.SetOutput(io.Discard)

	teaProg := tea.NewProgram(interactiveModeUi)
	go func() {
		defer interactiveModeUi.Close()
		result, err := teaProg.Run()
		if err != nil {
			panic(err)
		}
		if err := result.(*tui.InteractiveUI).Err(); err != nil {
			panic(err)
		}
		fmt.Println("exiting...")
		os.Exit(0)
	}()

	return interactiveModeUi.GetCodeSnippet, nil
}

func fetchQueryHandler(executeFn func() (string, error)) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		query, err := executeFn()
		if err != nil {
			log.Printf("error executing user code: %v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}
		queryParams := r.URL.Query()
		expr := queryParams.Get("g0.expr")

		if query == expr {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		log.Printf("query mismatch, reloading")

		queryParams.Set("g0.expr", query)

		response := map[string]any{
			"query": queryParams.Encode(),
		}

		res, err := json.Marshal(response)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusOK)
		w.Header().Add("Content-Type", "application/json")
		if _, err := w.Write(res); err != nil {
			log.Printf("error writing response: %v", err)
		}
	}
}

func proxyVitoriaMetrics(VMUrl string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		log.Printf("%v", r.URL.Path)
		finalURL := fmt.Sprintf("%s%s", VMUrl, r.URL.Path)
		log.Printf("proxy: %s", finalURL)
		req, err := http.NewRequest(r.Method, finalURL, r.Body)
		if r.Body != nil {
			defer r.Body.Close()
		}
		if err != nil {
			log.Printf("error creating proxy request: %v", err)
			w.WriteHeader(500)
			return
		}

		req.Header = r.Header.Clone()
		req.Header.Del("host")

		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			log.Printf("error executing proxy request: %v", err)
			w.WriteHeader(500)
			return
		}

		exlcude := map[string]struct{}{
			"content-encoding":  {},
			"content-length":    {},
			"transfer-encoding": {},
			"connection":        {},
		}

		for k, vals := range resp.Header {
			if _, ok := exlcude[k]; ok {
				continue
			}
			w.Header().Del(k)
			for _, v := range vals {
				w.Header().Add(k, v)
			}
		}

		w.WriteHeader(resp.StatusCode)

		if _, err := io.Copy(w, resp.Body); err != nil {
			return
		}
	}
}
