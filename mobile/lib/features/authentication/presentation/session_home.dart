import 'package:flutter/material.dart';

import '../../../shared/models/user.dart';
import 'auth_controller.dart';

class SessionHome extends StatelessWidget {
  const SessionHome({required this.controller, required this.doctorsScreen, super.key});

  final AuthController controller;
  final Widget doctorsScreen;

  @override
  Widget build(BuildContext context) {
    final user = controller.user!;
    final profile = user.profile;
    return Scaffold(
      appBar: AppBar(
        title: const Text('صحتي'),
        actions: [
          IconButton(
            tooltip: 'تسجيل الخروج',
            onPressed: controller.isBusy ? null : controller.logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('مرحباً بك', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          Text(user.email),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('الملف الشخصي', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 12),
                  _InfoRow(label: 'الاسم', value: _profileName(user)),
                  _InfoRow(label: 'الدور النشط', value: user.userType),
                  _InfoRow(
                    label: 'الأدوار المعتمدة',
                    value: user.activeRoles.isEmpty ? 'patient' : user.activeRoles.join('، '),
                  ),
                  if (profile['phone'] != null) _InfoRow(label: 'الهاتف', value: '${profile['phone']}'),
                  if (profile['city'] != null) _InfoRow(label: 'المدينة', value: '${profile['city']}'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              leading: const CircleAvatar(child: Icon(Icons.medical_services_outlined)),
              title: const Text('الأطباء'),
              subtitle: const Text('ابحث عن طبيب حسب الاسم أو التخصص'),
              trailing: const Icon(Icons.chevron_left),
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => doctorsScreen),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _profileName(User user) {
    final profile = user.profile;
    final first = '${profile['first_name'] ?? ''}'.trim();
    final last = '${profile['last_name'] ?? ''}'.trim();
    final name = '$first $last'.trim();
    return name.isEmpty ? user.email : name;
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text('$label: ', style: const TextStyle(fontWeight: FontWeight.w600)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
