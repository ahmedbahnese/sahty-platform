import 'package:flutter/material.dart';

import '../../features/authentication/presentation/auth_controller.dart';
import '../../features/authentication/presentation/login_screen.dart';
import '../../features/authentication/presentation/session_home.dart';

class AppRouter extends StatelessWidget {
  const AppRouter({required this.authController, super.key});

  final AuthController authController;

  @override
  Widget build(BuildContext context) {
    if (authController.isRestoring) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return authController.isAuthenticated
        ? SessionHome(controller: authController)
        : LoginScreen(controller: authController);
  }
}
