package dev.fastparse;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

final class NativeLibraryLoader {
    private static volatile boolean loaded;
    private static String loadedCorePath;

    private NativeLibraryLoader() {}

    static synchronized void load(String explicitCorePath, String explicitJniPath) {
        if (loaded) {
            return;
        }

        String corePath = firstNonEmpty(explicitCorePath, System.getProperty("fastparse.library.path"), System.getenv("FASTPARSE_LIBRARY_PATH"), System.getenv("TSMP_LIBRARY_PATH"));
        String jniPath = firstNonEmpty(explicitJniPath, System.getProperty("fastparse.jni.library.path"), System.getenv("FASTPARSE_JNI_LIBRARY_PATH"));

        try {
            if (corePath == null) {
                corePath = extractBundled(nativeResourceName(coreLibraryFileName()));
            }
            if (jniPath == null) {
                jniPath = extractBundled(nativeResourceName(jniLibraryFileName()));
            }
            System.load(jniPath);
            NativeBridge.nativeInitialize(corePath);
            loadedCorePath = corePath;
            loaded = true;
        } catch (IOException ex) {
            throw new FastParseException(loaderError("Unable to extract/load FastParse native libraries", corePath, jniPath, ex));
        } catch (UnsatisfiedLinkError ex) {
            throw new FastParseException(loaderError("Unable to load FastParse JNI/native libraries", corePath, jniPath, ex));
        }
    }

    static String loadedCorePath() {
        return loadedCorePath;
    }

    private static String nativeResourceName(String fileName) {
        return "/dev/fastparse/native/" + rid() + "/" + fileName;
    }

    private static String extractBundled(String resourceName) throws IOException {
        InputStream stream = NativeLibraryLoader.class.getResourceAsStream(resourceName);
        if (stream == null) {
            throw new IOException("Missing bundled native resource " + resourceName + " for " + osName() + "/" + archName());
        }
        File dir = new File(System.getProperty("java.io.tmpdir"), "fastparse-java/" + rid());
        if (!dir.isDirectory() && !dir.mkdirs()) {
            throw new IOException("Cannot create native extraction directory: " + dir);
        }
        File out = new File(dir, resourceName.substring(resourceName.lastIndexOf('/') + 1));
        byte[] bytes = readAll(stream);
        if (!out.isFile() || !sha256(bytes).equals(sha256(Files.readAllBytes(out.toPath())))) {
            File tmp = new File(out.getAbsolutePath() + ".tmp");
            FileOutputStream fos = new FileOutputStream(tmp);
            try {
                fos.write(bytes);
            } finally {
                fos.close();
            }
            if (!tmp.renameTo(out)) {
                Files.deleteIfExists(out.toPath());
                if (!tmp.renameTo(out)) {
                    throw new IOException("Cannot move native library into place: " + out);
                }
            }
        }
        out.deleteOnExit();
        return out.getAbsolutePath();
    }

    private static byte[] readAll(InputStream stream) throws IOException {
        try {
            byte[] buffer = new byte[8192];
            int read;
            java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
            while ((read = stream.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
            return out.toByteArray();
        } finally {
            stream.close();
        }
    }

    private static String sha256(byte[] bytes) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(bytes);
            StringBuilder builder = new StringBuilder(hash.length * 2);
            for (byte b : hash) {
                builder.append(String.format("%02x", b & 0xff));
            }
            return builder.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    private static String loaderError(String title, String corePath, String jniPath, Throwable throwable) {
        return title + "\nOS: " + osName() + "\nArch: " + archName() + "\nRID: " + rid()
                + "\nCore path: " + corePath + "\nJNI path: " + jniPath + "\nCause: " + throwable.getMessage();
    }

    private static String firstNonEmpty(String... values) {
        if (values == null) {
            return null;
        }
        for (String value : values) {
            if (value != null && !value.trim().isEmpty()) {
                return value;
            }
        }
        return null;
    }

    private static String coreLibraryFileName() {
        if (isWindows()) return "fastparse.dll";
        if (isMac()) return "libfastparse.dylib";
        return "libfastparse.so";
    }

    private static String jniLibraryFileName() {
        if (isWindows()) return "fastparse_jni.dll";
        if (isMac()) return "libfastparse_jni.dylib";
        return "libfastparse_jni.so";
    }

    private static String rid() {
        return osRid() + "-" + archRid();
    }

    private static String osRid() {
        if (isWindows()) return "windows";
        if (isMac()) return "macos";
        return "linux";
    }

    private static String archRid() {
        String arch = archName();
        if (arch.equals("aarch64") || arch.equals("arm64")) return "arm64";
        if (arch.equals("x86_64") || arch.equals("amd64")) return "x64";
        return arch;
    }

    private static boolean isWindows() { return osName().contains("win"); }
    private static boolean isMac() { return osName().contains("mac") || osName().contains("darwin"); }
    private static String osName() { return System.getProperty("os.name", "").toLowerCase(); }
    private static String archName() { return System.getProperty("os.arch", "").toLowerCase(); }
}
