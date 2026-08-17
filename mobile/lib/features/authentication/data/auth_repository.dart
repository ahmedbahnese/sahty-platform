import '../../../core/network/api_client.dart';
import '../../../core/security/session_manager.dart';
import '../../../shared/models/user.dart';

class AuthResult {
  const AuthResult({required this.token, required this.user});

  final String token;
  final User user;
}

class AuthRepository {
  AuthRepository(this._api, this._sessionManager);

  final ApiClient _api;
  final SessionManager _sessionManager;

  Future<AuthResult> login({
    required String email,
    required String password,
  }) async {
    final data =
        await _api.post(
              '/auth/login',
              body: {'email': email, 'password': password},
            )
            as Map<String, dynamic>;
    return _saveResult(data);
  }

  Future<User> restore() async {
    final data = await _api.get('/auth/profile') as Map<String, dynamic>;
    final userJson = data['user'] is Map
        ? Map<String, dynamic>.from(data['user'] as Map)
        : data;
    final user = User.fromJson(userJson);
    final token = await _sessionManager.readToken();
    if (token == null) throw StateError('Missing saved token');
    await _sessionManager.save(token: token, user: user);
    return user;
  }

  Future<void> logout() async {
    try {
      await _api.post('/auth/logout');
    } finally {
      await _sessionManager.clear();
    }
  }

  Future<void> clearLocalSession() => _sessionManager.clear();

  Future<User> switchRole(String role) async {
    final data =
        await _api.post('/auth/switch-role', body: {'role': role})
            as Map<String, dynamic>;
    return _saveResult(data).then((result) => result.user);
  }

  Future<AuthResult> _saveResult(Map<String, dynamic> data) async {
    final token = data['token'] as String?;
    final userJson = data['user'];
    if (token == null || userJson is! Map) {
      throw StateError('Authentication response is missing token or user');
    }
    final user = User.fromJson(Map<String, dynamic>.from(userJson));
    await _sessionManager.save(token: token, user: user);
    return AuthResult(token: token, user: user);
  }
}
