import 'dart:convert';

import '../storage/secure_storage_service.dart';
import '../../shared/models/user.dart';

class SessionManager {
  SessionManager(this._storage);

  static const _tokenKey = 'sahty.auth.token';
  static const _userKey = 'sahty.auth.user';

  final KeyValueStore _storage;

  Future<String?> readToken() => _storage.read(_tokenKey);

  Future<User?> readUser() async {
    final raw = await _storage.read(_userKey);
    if (raw == null) return null;
    try {
      return User.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } on Object {
      await clear();
      return null;
    }
  }

  Future<void> save({required String token, required User user}) async {
    await _storage.write(_tokenKey, token);
    await _storage.write(_userKey, jsonEncode(user.toJson()));
  }

  Future<void> clear() async {
    await _storage.delete(_tokenKey);
    await _storage.delete(_userKey);
  }
}
