package dev.fastparse;

/** Exception thrown when FastParse native loading or native calls fail. */
public class FastParseException extends RuntimeException {
    private final int apiStatus;
    private final int nativeStatus;

    public FastParseException(String message) {
        this(0, 0, message);
    }

    public FastParseException(int apiStatus, int nativeStatus, String message) {
        super(message);
        this.apiStatus = apiStatus;
        this.nativeStatus = nativeStatus;
    }

    public int getApiStatus() { return apiStatus; }
    public int getNativeStatus() { return nativeStatus; }
}
