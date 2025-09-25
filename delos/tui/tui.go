package tui

import (
	"fmt"
	"strings"

	"github.com/VictoriaMetrics/metricsql"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/hudson-trading/heracles-ql.git/delos/python"
)

type InteractiveUI struct {
	tmpFile   *embeddedEditorFile
	executor  *python.Executor
	serverURL string
	err       error
}

func NewInteractiveUI(executor *python.Executor, serverURL string) (*InteractiveUI, error) {
	tmpFile, err := newEmbeddedEditorFile()
	if err != nil {
		return nil, err
	}
	return &InteractiveUI{
		executor:  executor,
		tmpFile:   tmpFile,
		serverURL: serverURL,
	}, nil
}

func (i *InteractiveUI) Init() tea.Cmd {
	return nil
}

func (i *InteractiveUI) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return i, tea.Quit
		case "e":
			return i, i.tmpFile.showEditor()
		}
	case editorMsg:
		if msg.err != nil {
			newModel := *i
			newModel.err = msg.err
			return &newModel, tea.Quit
		}
	}

	return i, nil
}

func (i *InteractiveUI) getStatusMsg() string {
	codeSnippet, err := i.GetCodeSnippet()
	if err != nil {
		return fmt.Sprintf("ERROR: failed to exectue user code: %v", err)
	}

	formatted, err := metricsql.Prettify(codeSnippet)
	if err != nil {
		return fmt.Sprintf("ERROR: could not format query: %v", err)
	}

	return fmt.Sprintf("QUERY:\n%s", formatted)
}

func (i *InteractiveUI) View() string {
	sb := strings.Builder{}
	sb.WriteString(" -- Delos Interactive Mode --\n")
	sb.WriteString("-> ")
	sb.WriteString(i.serverURL)
	sb.WriteString(" <-\n")
	sb.WriteString(i.getStatusMsg())
	sb.WriteString("\n")
	sb.WriteString("Enter command:\n")
	sb.WriteString("    'q' - exit\n")
	sb.WriteString("    'e' - edit\n")

	return sb.String()
}

func (i *InteractiveUI) GetCodeSnippet() (string, error) {
	return i.executor.ExecuteFile(i.tmpFile.path())
}

func (i *InteractiveUI) Close() error {
	return i.tmpFile.Close()
}

func (i *InteractiveUI) Err() error {
	return i.err
}
