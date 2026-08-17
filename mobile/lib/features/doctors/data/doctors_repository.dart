import '../../../core/network/api_client.dart';

class DoctorsRepository {
  DoctorsRepository(this._api);

  final ApiClient _api;

  Future<List<Map<String, dynamic>>> search({
    String? query,
    String? specialty,
  }) async {
    final response = await _api.get(
      '/doctors',
      queryParameters: {
        'per_page': '50',
        if (query != null && query.trim().isNotEmpty) 'search': query.trim(),
        if (specialty != null && specialty.trim().isNotEmpty)
          'specialty': specialty.trim(),
      },
    );
    final raw = response is Map ? response['doctors'] : response;
    if (raw is! List) return const [];
    return raw
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList(growable: false);
  }
}
