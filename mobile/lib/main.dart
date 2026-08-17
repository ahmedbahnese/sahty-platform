import 'package:flutter/material.dart';

import 'core/config/app_config.dart';
import 'core/network/api_client.dart';
import 'core/routing/app_router.dart';
import 'core/security/session_manager.dart';
import 'core/storage/secure_storage_service.dart';
import 'core/theme/app_theme.dart';
import 'features/authentication/data/auth_repository.dart';
import 'features/authentication/presentation/auth_controller.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final storage = SecureStorageService();
  final sessionManager = SessionManager(storage);
  final apiClient = ApiClient(
    baseUrl: AppConfig.apiBaseUrl,
    sessionManager: sessionManager,
  );
  final authController = AuthController(
    AuthRepository(apiClient, sessionManager),
  );
  apiClient.onUnauthorized = authController.expireSession;
  await authController.restoreSession();

  runApp(SahtyApp(authController: authController, apiClient: apiClient));
}

class SahtyApp extends StatelessWidget {
  const SahtyApp({required this.authController, required this.apiClient, super.key});

  final AuthController authController;
  final ApiClient apiClient;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: authController,
      builder: (context, _) {
        return MaterialApp(
          title: 'صحتي',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light(),
          locale: const Locale('ar'),
          supportedLocales: const [Locale('ar'), Locale('en')],
          home: AppRouter(authController: authController, apiClient: apiClient),
        );
      },
    );
  }
}
