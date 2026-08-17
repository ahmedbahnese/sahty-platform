import 'package:flutter/material.dart';

class AppTheme {
  const AppTheme._();

  static const _teal = Color(0xFF007F7B);
  static const _navy = Color(0xFF103B4A);

  static ThemeData light() {
    final scheme =
        ColorScheme.fromSeed(
          seedColor: _teal,
          brightness: Brightness.light,
        ).copyWith(
          primary: _teal,
          secondary: const Color(0xFF21A179),
          surface: const Color(0xFFF7FAFA),
        );
    return ThemeData(
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      useMaterial3: true,
      fontFamily: 'Arial',
      textTheme: const TextTheme(
        headlineSmall: TextStyle(color: _navy, fontWeight: FontWeight.w700),
        titleLarge: TextStyle(color: _navy, fontWeight: FontWeight.w700),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFD8E6E5)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: _teal, width: 2),
        ),
      ),
    );
  }
}
