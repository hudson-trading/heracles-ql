package python

import (
	"embed"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"text/template"
)

//go:embed templates/*
var templateFs embed.FS

//go:embed interface.py
var pyInterfaceCode string

type ExecutionMode int

const (
	SnippetExecutionMode ExecutionMode = iota
	FileExecutionMode
)

const querySigil = "__DELOS_QUERY_STARTS:"

type SnippetExecutionContext struct {
	Imports []string
	Code    string
}

type Executor struct {
	executionTemplates *template.Template
	interfaceCode      string
	pythonCmd          string
}

func NewExecutor(pythonCmd string) (*Executor, error) {
	executionTemplates, err := template.ParseFS(templateFs, "templates/*.tmpl")
	if err != nil {
		return nil, fmt.Errorf("failed to load execution templates: %v", err)
	}

	return &Executor{
		executionTemplates: executionTemplates,
		interfaceCode:      pyInterfaceCode,
		pythonCmd:          pythonCmd,
	}, nil
}

func (e *Executor) executePython(code string) (string, error) {
	cmd := exec.Command(e.pythonCmd, "-c", e.interfaceCode, code)

	var stdout, stderr strings.Builder
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Start()
	if err != nil {
		return "", fmt.Errorf("failed to execute python: %v", err)
	}

	if err := cmd.Wait(); err != nil {
		log.Printf("python execution error: %v %s", err, stderr.String())
		return "", fmt.Errorf("execution error: %v", err)
	}

	sigilIdx := strings.Index(stdout.String(), querySigil)
	if sigilIdx == -1 {
		return "", fmt.Errorf("failed to find query siginal in output: %s", stdout.String())
	}

	return stdout.String()[sigilIdx+len(querySigil):], nil
}

func (e *Executor) ExecuteSnippet(snippetCtx SnippetExecutionContext) (string, error) {
	var sb strings.Builder
	err := e.executionTemplates.ExecuteTemplate(&sb, "snippet.py.tmpl", snippetCtx)
	if err != nil {
		return "", fmt.Errorf("error rendering snippet tempalte: %v", err)
	}

	return e.executePython(sb.String())
}

func (e *Executor) ExecuteFile(filePath string) (string, error) {
	contents, err := os.ReadFile(filePath)
	if err != nil {
		return "", fmt.Errorf("failed to read file: %v", err)
	}

	return e.executePython(string(contents))
}
