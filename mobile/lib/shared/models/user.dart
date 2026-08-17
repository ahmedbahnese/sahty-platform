class User {
  const User({
    required this.id,
    required this.email,
    required this.userType,
    this.username,
    this.isActive = true,
    this.activeRoles = const [],
  });

  factory User.fromJson(Map<String, dynamic> json) {
    final roles = json['active_roles'];
    return User(
      id: _asInt(json['id']) ?? 0,
      email: json['email'] as String? ?? '',
      username: json['username'] as String?,
      userType: json['user_type'] as String? ?? 'patient',
      isActive: json['is_active'] as bool? ?? true,
      activeRoles: roles is List
          ? roles.whereType<String>().toList(growable: false)
          : const [],
    );
  }

  final int id;
  final String email;
  final String? username;
  final String userType;
  final bool isActive;
  final List<String> activeRoles;

  bool hasRole(String role) => activeRoles.contains(role);

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'username': username,
    'user_type': userType,
    'is_active': isActive,
    'active_roles': activeRoles,
  };

  static int? _asInt(Object? value) {
    if (value is int) return value;
    return int.tryParse('$value');
  }
}
