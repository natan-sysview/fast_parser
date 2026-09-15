#include <jni.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "tsmp.h"

#ifdef _WIN32
#include <windows.h>
static HMODULE g_core_handle = NULL;
#else
#include <dlfcn.h>
static void *g_core_handle = NULL;
#endif

static const char *(*p_fastparse_version)(void) = NULL;
static int (*p_fastparse_parse_v2)(const unsigned char *, size_t, const TsmpOptionsV2 *, TsmpResult *) = NULL;
static int (*p_fastparse_query)(const unsigned char *, size_t, const unsigned char *, size_t, const TsmpQueryOptions *, TsmpResult *) = NULL;
static void (*p_fastparse_result_free)(TsmpResult *) = NULL;
static int (*p_fastparse_load_language_extension)(const char *, FastParseLanguageLoadResult *) = NULL;
static int (*p_fastparse_language_available)(const char *) = NULL;
static void (*p_fastparse_language_load_result_free)(FastParseLanguageLoadResult *) = NULL;

static void throw_fastparse(JNIEnv *env, int api_status, int native_status, const char *message) {
    jclass cls = (*env)->FindClass(env, "dev/fastparse/FastParseException");
    if (cls == NULL) {
        return;
    }
    jmethodID ctor = (*env)->GetMethodID(env, cls, "<init>", "(IILjava/lang/String;)V");
    if (ctor == NULL) {
        return;
    }
    jstring jmsg = (*env)->NewStringUTF(env, message == NULL ? "FastParse native error" : message);
    jobject ex = (*env)->NewObject(env, cls, ctor, (jint)api_status, (jint)native_status, jmsg);
    if (ex != NULL) {
        (*env)->Throw(env, (jthrowable)ex);
    }
}

static char *jstring_to_utf8(JNIEnv *env, jstring value) {
    if (value == NULL) {
        return NULL;
    }
    const char *tmp = (*env)->GetStringUTFChars(env, value, NULL);
    if (tmp == NULL) {
        return NULL;
    }
    size_t len = strlen(tmp);
    char *copy = (char *)malloc(len + 1);
    if (copy != NULL) {
        memcpy(copy, tmp, len + 1);
    }
    (*env)->ReleaseStringUTFChars(env, value, tmp);
    return copy;
}

static void *load_symbol(const char *name) {
#ifdef _WIN32
    return (void *)GetProcAddress(g_core_handle, name);
#else
    return dlsym(g_core_handle, name);
#endif
}

static int ensure_initialized(JNIEnv *env) {
    if (g_core_handle == NULL || p_fastparse_version == NULL || p_fastparse_parse_v2 == NULL ||
        p_fastparse_query == NULL || p_fastparse_result_free == NULL) {
        throw_fastparse(env, 0, 0, "FastParse JNI bridge is not initialized");
        return 0;
    }
    return 1;
}

static jobject new_parse_result(JNIEnv *env, unsigned char *data, size_t length, size_t node_count, int format) {
    jclass cls = (*env)->FindClass(env, "dev/fastparse/ParseResult");
    if (cls == NULL) {
        return NULL;
    }
    jmethodID ctor = (*env)->GetMethodID(env, cls, "<init>", "([BJI)V");
    if (ctor == NULL) {
        return NULL;
    }
    if (length > INT32_MAX) {
        throw_fastparse(env, 0, 0, "FastParse output is too large for a Java byte array");
        return NULL;
    }
    jbyteArray bytes = (*env)->NewByteArray(env, (jsize)length);
    if (bytes == NULL) {
        return NULL;
    }
    if (length > 0 && data != NULL) {
        (*env)->SetByteArrayRegion(env, bytes, 0, (jsize)length, (const jbyte *)data);
    }
    return (*env)->NewObject(env, cls, ctor, bytes, (jlong)node_count, (jint)format);
}

JNIEXPORT void JNICALL Java_dev_fastparse_NativeBridge_nativeInitialize(JNIEnv *env, jclass cls, jstring corePath) {
    (void)cls;
    if (g_core_handle != NULL) {
        return;
    }
#ifdef _WIN32
    const jchar *path = (*env)->GetStringChars(env, corePath, NULL);
    if (path == NULL) {
        throw_fastparse(env, 0, 0, "core library path is required");
        return;
    }
    g_core_handle = LoadLibraryW((const wchar_t *)path);
    (*env)->ReleaseStringChars(env, corePath, path);
    if (g_core_handle == NULL) {
        throw_fastparse(env, 0, 0, "Unable to load FastParse core library with LoadLibraryW");
        return;
    }
#else
    char *path = jstring_to_utf8(env, corePath);
    if (path == NULL) {
        throw_fastparse(env, 0, 0, "core library path is required");
        return;
    }
    g_core_handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    free(path);
    if (g_core_handle == NULL) {
        throw_fastparse(env, 0, 0, dlerror());
        return;
    }
#endif
    p_fastparse_version = (const char *(*)(void))load_symbol("fastparse_version");
    p_fastparse_parse_v2 = (int (*)(const unsigned char *, size_t, const TsmpOptionsV2 *, TsmpResult *))load_symbol("fastparse_parse_v2");
    p_fastparse_query = (int (*)(const unsigned char *, size_t, const unsigned char *, size_t, const TsmpQueryOptions *, TsmpResult *))load_symbol("fastparse_query");
    p_fastparse_result_free = (void (*)(TsmpResult *))load_symbol("fastparse_result_free");
    p_fastparse_load_language_extension = (int (*)(const char *, FastParseLanguageLoadResult *))load_symbol("fastparse_load_language_extension");
    p_fastparse_language_available = (int (*)(const char *))load_symbol("fastparse_language_available");
    p_fastparse_language_load_result_free = (void (*)(FastParseLanguageLoadResult *))load_symbol("fastparse_language_load_result_free");

    if (p_fastparse_version == NULL || p_fastparse_parse_v2 == NULL || p_fastparse_query == NULL ||
        p_fastparse_result_free == NULL || p_fastparse_load_language_extension == NULL ||
        p_fastparse_language_available == NULL || p_fastparse_language_load_result_free == NULL) {
        throw_fastparse(env, 0, 0, "FastParse core library is missing required native symbols");
    }
}

JNIEXPORT jstring JNICALL Java_dev_fastparse_NativeBridge_nativeVersion(JNIEnv *env, jclass cls) {
    (void)cls;
    if (!ensure_initialized(env)) return NULL;
    return (*env)->NewStringUTF(env, p_fastparse_version());
}

JNIEXPORT jboolean JNICALL Java_dev_fastparse_NativeBridge_nativeLanguageAvailable(JNIEnv *env, jclass cls, jstring language) {
    (void)cls;
    if (!ensure_initialized(env)) return JNI_FALSE;
    char *lang = jstring_to_utf8(env, language);
    if (lang == NULL) return JNI_FALSE;
    int available = p_fastparse_language_available(lang);
    free(lang);
    return available ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jobjectArray JNICALL Java_dev_fastparse_NativeBridge_nativeLoadLanguageExtension(JNIEnv *env, jclass cls, jstring pathValue) {
    (void)cls;
    if (!ensure_initialized(env)) return NULL;
    char *path = jstring_to_utf8(env, pathValue);
    if (path == NULL) {
        throw_fastparse(env, 0, 0, "language extension path is required");
        return NULL;
    }
    FastParseLanguageLoadResult result;
    memset(&result, 0, sizeof(result));
    int status = p_fastparse_load_language_extension(path, &result);
    free(path);
    if (status != 0 || result.status != 0) {
        const char *msg = result.error_message == NULL ? "Unable to load FastParse language extension" : result.error_message;
        throw_fastparse(env, status, result.status, msg);
        p_fastparse_language_load_result_free(&result);
        return NULL;
    }
    jclass stringCls = (*env)->FindClass(env, "java/lang/String");
    jobjectArray arr = (*env)->NewObjectArray(env, 2, stringCls, NULL);
    if (arr != NULL) {
        (*env)->SetObjectArrayElement(env, arr, 0, (*env)->NewStringUTF(env, result.language == NULL ? "" : result.language));
        (*env)->SetObjectArrayElement(env, arr, 1, (*env)->NewStringUTF(env, result.display_name == NULL ? "" : result.display_name));
    }
    p_fastparse_language_load_result_free(&result);
    return arr;
}

JNIEXPORT jobject JNICALL Java_dev_fastparse_NativeBridge_nativeParse(
    JNIEnv *env, jclass cls, jbyteArray source, jstring language, jint format, jstring includeRules,
    jlong fields, jboolean includeTokens, jboolean pretty, jint normalization) {
    (void)cls;
    if (!ensure_initialized(env)) return NULL;
    jsize source_len = source == NULL ? 0 : (*env)->GetArrayLength(env, source);
    jbyte *source_ptr = source_len == 0 ? NULL : (*env)->GetByteArrayElements(env, source, NULL);
    char *lang = jstring_to_utf8(env, language);
    char *rules = jstring_to_utf8(env, includeRules);
    TsmpOptionsV2 options;
    memset(&options, 0, sizeof(options));
    options.language = lang == NULL ? "java" : lang;
    options.format = (TsmpFormat)format;
    options.include_rules = rules;
    options.fields = (unsigned int)fields;
    options.include_tokens = includeTokens ? 1 : 0;
    options.pretty = pretty ? 1 : 0;
    options.normalization = (TsmpNormalization)normalization;
    TsmpResult result;
    memset(&result, 0, sizeof(result));
    int status = p_fastparse_parse_v2((const unsigned char *)source_ptr, (size_t)source_len, &options, &result);
    if (source_ptr != NULL) {
        (*env)->ReleaseByteArrayElements(env, source, source_ptr, JNI_ABORT);
    }
    free(lang);
    free(rules);
    if (status != 0 || result.status != 0) {
        const char *msg = result.error_message == NULL ? "FastParse parse failed" : result.error_message;
        throw_fastparse(env, status, result.status, msg);
        p_fastparse_result_free(&result);
        return NULL;
    }
    jobject out = new_parse_result(env, result.data, result.length, result.node_count, format);
    p_fastparse_result_free(&result);
    return out;
}

JNIEXPORT jobject JNICALL Java_dev_fastparse_NativeBridge_nativeQuery(
    JNIEnv *env, jclass cls, jbyteArray source, jbyteArray query, jstring language, jint format,
    jlong fields, jlong maxMatches, jlong maxCaptures, jboolean includePattern, jboolean pretty, jint normalization) {
    (void)cls;
    if (!ensure_initialized(env)) return NULL;
    jsize source_len = source == NULL ? 0 : (*env)->GetArrayLength(env, source);
    jsize query_len = query == NULL ? 0 : (*env)->GetArrayLength(env, query);
    jbyte *source_ptr = source_len == 0 ? NULL : (*env)->GetByteArrayElements(env, source, NULL);
    jbyte *query_ptr = query_len == 0 ? NULL : (*env)->GetByteArrayElements(env, query, NULL);
    char *lang = jstring_to_utf8(env, language);
    TsmpQueryOptions options;
    memset(&options, 0, sizeof(options));
    options.language = lang == NULL ? "java" : lang;
    options.format = (TsmpFormat)format;
    options.fields = (unsigned int)fields;
    options.max_matches = (size_t)maxMatches;
    options.max_captures = (size_t)maxCaptures;
    options.include_pattern = includePattern ? 1 : 0;
    options.pretty = pretty ? 1 : 0;
    options.normalization = (TsmpNormalization)normalization;
    TsmpResult result;
    memset(&result, 0, sizeof(result));
    int status = p_fastparse_query((const unsigned char *)source_ptr, (size_t)source_len,
                                   (const unsigned char *)query_ptr, (size_t)query_len,
                                   &options, &result);
    if (source_ptr != NULL) (*env)->ReleaseByteArrayElements(env, source, source_ptr, JNI_ABORT);
    if (query_ptr != NULL) (*env)->ReleaseByteArrayElements(env, query, query_ptr, JNI_ABORT);
    free(lang);
    if (status != 0 || result.status != 0) {
        const char *msg = result.error_message == NULL ? "FastParse query failed" : result.error_message;
        throw_fastparse(env, status, result.status, msg);
        p_fastparse_result_free(&result);
        return NULL;
    }
    jobject out = new_parse_result(env, result.data, result.length, result.node_count, format);
    p_fastparse_result_free(&result);
    return out;
}
