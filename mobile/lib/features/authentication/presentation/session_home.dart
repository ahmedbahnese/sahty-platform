import 'package:flutter/material.dart';

import 'auth_controller.dart';

class SessionHome extends StatelessWidget {
  const SessionHome({required this.controller, super.key});

  final AuthController controller;

  @override
  Widget build(BuildContext context) {
    final user = controller.user!;
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
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'جلسة المصادقة',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),
                  _InfoRow(label: 'الدور النشط', value: user.userType),
                  _InfoRow(
                    label: 'الأدوار المعتمدة',
                    value: user.activeRoles.isEmpty
                        ? 'patient'
                        : user.activeRoles.join('، '),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Text(
                'تم تجهيز طبقة المصادقة، الجلسة، الشبكة، التخزين الآمن، والمسارات الأساسية. '
                'سيتم توصيل وحدات الرعاية الصحية فقط بعد التحقق من واجهاتها الفعلية.',
              ),
            ),
          ),
        ],
      ),
    );
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
