import 'package:flutter_test/flutter_test.dart';
import 'package:sahty_mobile/core/security/session_manager.dart';
import 'package:sahty_mobile/core/storage/secure_storage_service.dart';
import 'package:sahty_mobile/shared/models/user.dart';

void main() {
  test(
    'persists and clears token and user without exposing credentials',
    () async {
      final manager = SessionManager(MemorySecureStorage());
      const user = User(
        id: 1,
        email: 'patient@example.com',
        userType: 'patient',
        activeRoles: ['patient'],
      );

      await manager.save(token: 'test-token', user: user);
      expect(await manager.readToken(), 'test-token');
      expect((await manager.readUser())?.email, user.email);

      await manager.clear();
      expect(await manager.readToken(), isNull);
      expect(await manager.readUser(), isNull);
    },
  );
}
