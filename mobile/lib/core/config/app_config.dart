class AppConfig {
  const AppConfig._();

  /// Override with:
  /// flutter run --dart-define=API_BASE_URL=https://api.example.com/api
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:5001/api',
  );
}
