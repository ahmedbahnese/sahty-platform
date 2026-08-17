import 'package:flutter/foundation.dart';

import '../../../core/errors/app_exception.dart';
import '../../../shared/models/user.dart';
import '../data/auth_repository.dart';

class AuthController extends ChangeNotifier {
  AuthController(this._repository);

  final AuthRepository _repository;

  User? user;
  bool isRestoring = true;
  bool isBusy = false;
  String? errorMessage;

  bool get isAuthenticated => user != null;

  Future<void> expireSession() async {
    await _repository.clearLocalSession();
    user = null;
    errorMessage = 'انتهت صلاحية الجلسة';
    notifyListeners();
  }

  Future<void> restoreSession() async {
    try {
      user = await _repository.restore();
    } on Object {
      user = null;
    } finally {
      isRestoring = false;
      notifyListeners();
    }
  }

  Future<bool> login({required String email, required String password}) async {
    return _run(() async {
      final result = await _repository.login(email: email, password: password);
      user = result.user;
    });
  }

  Future<void> logout() async {
    isBusy = true;
    notifyListeners();
    try {
      await _repository.logout();
    } finally {
      user = null;
      isBusy = false;
      notifyListeners();
    }
  }

  Future<bool> switchRole(String role) async {
    return _run(() async {
      if (user == null || !user!.hasRole(role)) {
        throw const AppException(message: 'هذا الدور غير معتمد لحسابك');
      }
      user = await _repository.switchRole(role);
    });
  }

  Future<bool> _run(Future<void> Function() action) async {
    isBusy = true;
    errorMessage = null;
    notifyListeners();
    try {
      await action();
      return true;
    } on AppException catch (error) {
      errorMessage = error.message;
      return false;
    } on Object {
      errorMessage = 'حدث خطأ غير متوقع';
      return false;
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }
}
