import 'package:flutter/material.dart';

import '../../../core/errors/app_exception.dart';
import '../data/doctors_repository.dart';

class DoctorsScreen extends StatefulWidget {
  const DoctorsScreen({required this.repository, super.key});

  final DoctorsRepository repository;

  @override
  State<DoctorsScreen> createState() => _DoctorsScreenState();
}

class _DoctorsScreenState extends State<DoctorsScreen> {
  final _searchController = TextEditingController();
  final _specialtyController = TextEditingController();
  List<Map<String, dynamic>> _doctors = const [];
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _specialtyController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final doctors = await widget.repository.search(
        query: _searchController.text,
        specialty: _specialtyController.text,
      );
      if (mounted) setState(() => _doctors = doctors);
    } on AppException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } on Object {
      if (mounted) setState(() => _error = 'تعذر تحميل الأطباء');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الأطباء')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextField(
              controller: _searchController,
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => _load(),
              decoration: const InputDecoration(
                labelText: 'بحث بالاسم أو المدينة',
                prefixIcon: Icon(Icons.search),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _specialtyController,
              textInputAction: TextInputAction.search,
              onSubmitted: (_) => _load(),
              decoration: const InputDecoration(
                labelText: 'التخصص',
                prefixIcon: Icon(Icons.medical_services_outlined),
              ),
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              onPressed: _loading ? null : _load,
              icon: const Icon(Icons.filter_alt_outlined),
              label: const Text('تطبيق البحث'),
            ),
            const SizedBox(height: 20),
            if (_loading) const Center(child: CircularProgressIndicator()),
            if (_error != null)
              Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(_error!),
                ),
              ),
            if (!_loading && _error == null && _doctors.isEmpty)
              const Center(child: Text('لا توجد نتائج مطابقة')),
            ..._doctors.map(_doctorCard),
          ],
        ),
      ),
    );
  }

  Widget _doctorCard(Map<String, dynamic> doctor) {
    final name = '${doctor['first_name'] ?? ''} ${doctor['last_name'] ?? ''}'.trim();
    return Card(
      child: ListTile(
        leading: const CircleAvatar(child: Icon(Icons.person)),
        title: Text(name.isEmpty ? 'طبيب' : name),
        subtitle: Text(
          '${doctor['specialization'] ?? 'تخصص غير محدد'}\n${doctor['clinic_name'] ?? doctor['clinic_address'] ?? ''}',
        ),
        isThreeLine: true,
        trailing: doctor['is_verified'] == true
            ? const Icon(Icons.verified, color: Colors.blue)
            : null,
      ),
    );
  }
}
