import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sahty_mobile/core/network/api_client.dart';
import 'package:sahty_mobile/core/security/session_manager.dart';
import 'package:sahty_mobile/core/storage/secure_storage_service.dart';
import 'package:sahty_mobile/shared/models/user.dart';

void main() {
  test('sends bearer authentication and decodes JSON', () async {
    final storage = MemorySecureStorage();
    final sessions = SessionManager(storage);
    await sessions.save(
      token: 'token-for-test',
      user: const User(
        id: 1,
        email: 'test@example.com',
        userType: 'patient',
        activeRoles: ['patient'],
      ),
    );
    final client = ApiClient(
      baseUrl: 'https://api.example.test/api',
      sessionManager: sessions,
      client: MockClient((request) async {
        expect(request.headers['authorization'], 'Bearer token-for-test');
        expect(request.url.path, '/api/profile');
        return http.Response(
          '{"ok":true}',
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );

    final response = await client.get('/profile') as Map<String, dynamic>;
    expect(response['ok'], isTrue);
  });

  test('calls unauthorized handler for a rejected API response', () async {
    var expired = false;
    final client = ApiClient(
      baseUrl: 'https://api.example.test/api',
      sessionManager: SessionManager(MemorySecureStorage()),
      onUnauthorized: () async => expired = true,
      client: MockClient(
        (_) async => http.Response(
          '{"message":"expired"}',
          401,
          headers: {'content-type': 'application/json'},
        ),
      ),
    );

    await expectLater(client.get('/profile'), throwsA(isA<Exception>()));
    expect(expired, isTrue);
  });
}
