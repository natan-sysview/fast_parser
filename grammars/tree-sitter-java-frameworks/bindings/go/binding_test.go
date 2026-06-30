package tree_sitter_java_frameworks_test

import (
	"testing"

	tree_sitter "github.com/tree-sitter/go-tree-sitter"
	tree_sitter_java_frameworks "github.com/tree-sitter/tree-sitter-java-frameworks/bindings/go"
)

func TestCanLoadGrammar(t *testing.T) {
	language := tree_sitter.NewLanguage(tree_sitter_java_frameworks.Language())
	if language == nil {
		t.Errorf("Error loading Java Frameworks grammar")
	}
}
