import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../errors/app_exception.dart';
import '../security/session_manager.dart';

typedef UnauthorizedHandler = Future<void> Function();

class ApiClient {
  ApiClient({
    required String baseUrl,
    required SessionManager sessionManager,
    http.Client? client,
    this.onUnauthorized,
    Duration timeout = const Duration(seconds: 30),
  }) : _baseUrl = baseUrl.replaceFirst(RegExp(r'/$'), ''),
       _sessionManager = sessionManager,
       _client = client ?? http.Client(),
       _timeout = timeout;

  final String _baseUrl;
  final SessionManager _sessionManager;
  final http.Client _client;
  UnauthorizedHandler? onUnauthorized;
  final Duration _timeout;

  Future<dynamic> get(String path, {Map<String, String>? queryParameters}) =>
      _send('GET', path, queryParameters: queryParameters);

  Future<dynamic> post(String path, {Object? body}) =>
      _send('POST', path, body: body);

  Future<dynamic> put(String path, {Object? body}) =>
      _send('PUT', path, body: body);

  Future<dynamic> delete(String path) => _send('DELETE', path);

  Future<dynamic> _send(
    String method,
    String path, {
    Object? body,
    Map<String, String>? queryParameters,
  }) async {
    final uri = _buildUri(path, queryParameters);
    final request = http.Request(method, uri);
    request.headers.addAll(await _headers());
    if (body != null) {
      request.headers['Content-Type'] = 'application/json';
      request.body = jsonEncode(body);
    }
    return _sendRequest(request);
  }

  Future<dynamic> upload(
    String path, {
    required String filePath,
    required String field,
    Map<String, String>? fields,
  }) async {
    final request = http.MultipartRequest('POST', _buildUri(path));
    request.headers.addAll(await _headers());
    if (fields != null) request.fields.addAll(fields);
    request.files.add(await http.MultipartFile.fromPath(field, filePath));
    return _sendRequest(request);
  }

  Future<List<int>> download(String path) async {
    try {
      final request = http.Request('GET', _buildUri(path));
      request.headers.addAll(await _headers());
      final response = await _perform(request);
      if (response.statusCode < 200 || response.statusCode >= 300) {
        await _throwForResponse(response);
      }
      return response.bodyBytes;
    } on AppException catch (error) {
      if (error.isUnauthorized) await onUnauthorized?.call();
      rethrow;
    } on TimeoutException {
      throw const AppException(message: 'انتهت مهلة الاتصال بالخادم');
    } on SocketException {
      throw const AppException(message: 'تعذر الاتصال بالخادم');
    }
  }

  Uri _buildUri(String path, [Map<String, String>? queryParameters]) {
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse(
      '$_baseUrl$normalizedPath',
    ).replace(queryParameters: queryParameters);
  }

  Future<Map<String, String>> _headers() async {
    final token = await _sessionManager.readToken();
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
    };
  }

  Future<dynamic> _sendRequest(http.BaseRequest request) async {
    try {
      final response = await _perform(request);
      if (response.statusCode < 200 || response.statusCode >= 300) {
        await _throwForResponse(response);
      }
      if (response.bodyBytes.isEmpty) return null;
      final contentType = response.headers['content-type'] ?? '';
      if (contentType.contains('application/json')) {
        return jsonDecode(response.body);
      }
      return response.body;
    } on AppException catch (error) {
      if (error.isUnauthorized) await onUnauthorized?.call();
      rethrow;
    } on TimeoutException {
      throw const AppException(message: 'انتهت مهلة الاتصال بالخادم');
    } on SocketException {
      throw const AppException(message: 'تعذر الاتصال بالخادم');
    } on FormatException {
      throw const AppException(message: 'استجابة غير صالحة من الخادم');
    }
  }

  Future<http.Response> _perform(http.BaseRequest request) async {
    final streamed = await _client.send(request).timeout(_timeout);
    return http.Response.fromStream(streamed);
  }

  Future<Never> _throwForResponse(http.Response response) async {
    String message = 'حدث خطأ أثناء الاتصال بالخادم';
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic> && decoded['message'] is String) {
        message = decoded['message'] as String;
      }
    } on Object {
      // Keep the safe generic message for non-JSON error responses.
    }
    throw AppException(message: message, statusCode: response.statusCode);
  }
}
