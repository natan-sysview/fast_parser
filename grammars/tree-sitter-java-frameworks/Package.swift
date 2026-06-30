// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "TreeSitterJavaFrameworks",
    products: [
        .library(name: "TreeSitterJavaFrameworks", targets: ["TreeSitterJavaFrameworks"]),
    ],
    dependencies: [
        .package(url: "https://github.com/ChimeHQ/SwiftTreeSitter", from: "0.8.0"),
    ],
    targets: [
        .target(
            name: "TreeSitterJavaFrameworks",
            dependencies: [],
            path: ".",
            sources: [
                "src/parser.c",
            ],
            resources: [
                .copy("queries")
            ],
            publicHeadersPath: "bindings/swift",
            cSettings: [.headerSearchPath("src")]
        ),
        .testTarget(
            name: "TreeSitterJavaFrameworksTests",
            dependencies: [
                "SwiftTreeSitter",
                "TreeSitterJavaFrameworks",
            ],
            path: "bindings/swift/TreeSitterJavaFrameworksTests"
        )
    ],
    cLanguageStandard: .c11
)
