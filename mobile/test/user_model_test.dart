import 'package:flutter_test/flutter_test.dart';
import 'package:sahty_mobile/shared/models/user.dart';

void main() {
  test('parses backend user and active roles', () {
    final user = User.fromJson({
      'id': 12,
      'email': 'patient@example.com',
      'user_type': 'doctor',
      'active_roles': ['patient', 'doctor'],
      'is_active': true,
    });

    expect(user.id, 12);
    expect(user.email, 'patient@example.com');
    expect(user.hasRole('doctor'), isTrue);
    expect(user.hasRole('admin'), isFalse);
  });
}
