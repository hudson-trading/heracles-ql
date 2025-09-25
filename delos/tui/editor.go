package tui

import (
	_ "embed"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
)

//go:embed initial_script.py
var initialFileContents string

type editorMsg struct {
	err error
}

type embeddedEditorFile struct {
	tmpFile *os.File
}

func newEmbeddedEditorFile() (*embeddedEditorFile, error) {
	tmpFile, err := os.CreateTemp("", "hqlsnip-*-.py")
	if err != nil {
		return nil, fmt.Errorf("failed to create temp file: %w", err)
	}

	_, err = tmpFile.WriteString(initialFileContents)
	if err != nil {
		return nil, fmt.Errorf("failed to write instructions to temp file: %w", err)
	}

	return &embeddedEditorFile{
		tmpFile: tmpFile,
	}, nil
}

func (e embeddedEditorFile) showEditor() tea.Cmd {
	editorCommand := os.Getenv("EDITOR")
	if editorCommand == "" {
		editorCommand = "vim"
	}

	cmd := strings.Join(
		[]string{editorCommand, fmt.Sprintf("\"%s\"", e.tmpFile.Name())},
		" ",
	)

	shellExecutable := os.Getenv("SHELL")
	if shellExecutable == "" {
		shellExecutable = "/bin/bash"
	}

	editorCmd := exec.Command(shellExecutable, "-c", cmd)
	return tea.ExecProcess(editorCmd, func(err error) tea.Msg {
		return editorMsg{
			err: err,
		}
	})
}

func (e *embeddedEditorFile) Close() error {
	closeErr := e.tmpFile.Close()
	removeErr := os.Remove(e.tmpFile.Name())

	if err := errors.Join(closeErr, removeErr); err != nil {
		return fmt.Errorf("failed to close or remove temp file: %w", err)
	}
	return nil
}

func (e *embeddedEditorFile) path() string {
	return e.tmpFile.Name()
}
