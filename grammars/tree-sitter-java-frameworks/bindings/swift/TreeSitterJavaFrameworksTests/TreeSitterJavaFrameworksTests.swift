import XCTest
import SwiftTreeSitter
import TreeSitterJavaFrameworks

final class TreeSitterJavaFrameworksTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_java_frameworks())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading Java Frameworks grammar")
    }
}
