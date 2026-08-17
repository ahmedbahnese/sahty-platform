import 'package:flutter/material.dart';

import '../../features/authentication/presentation/auth_controller.dart';
import '../../features/authentication/presentation/login_screen.dart';
import '../../features/authentication/presentation/session_home.dart';
import '../../features/doctors/data/doctors_repository.dart';
import '../../features/doctors/presentation/doctors_screen.dart';
import '../network/api_client.dart';

class AppRouter extends StatelessWidget {
  const AppRouter({required this.authController, required this.apiClient, super.key});

  final AuthController authController;
  final ApiClient apiClient;

  @override
  Widget build(BuildContext context) {
    if (authController.isRestoring) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return authController.isAuthenticated
        ? SessionHome(
            controller: authController,
            doctorsScreen: DoctorsScreen(repository: DoctorsRepository(apiClient)),
          )
        : LoginScreen(controller: authController);
  }
}
