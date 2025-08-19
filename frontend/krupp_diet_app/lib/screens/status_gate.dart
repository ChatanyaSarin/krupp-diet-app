import 'package:flutter/material.dart';
import '../services/api.dart';
import '../main.dart' show currentUsername;
import '../main.dart' show SetupScreen, InitialSuggestionsScreen, BiomarkerInputScreen;

class StatusGate extends StatefulWidget {
  const StatusGate({super.key});
  static const route = '/gate';

  @override
  State<StatusGate> createState() => _StatusGateState();
}

class _StatusGateState extends State<StatusGate> {
  late Future<Map<String, dynamic>> _statusFut;

  @override
  void initState() {
    super.initState();
    _statusFut = ApiService.getUserStatus(currentUsername);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _statusFut,
      builder: (ctx, snap) {
        if (!snap.hasData) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        final s = snap.data!;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (s['has_profile'] != true) {
            Navigator.pushReplacementNamed(context, SetupScreen.route);
          } else if (s['has_initial_feedback'] != true) {
            Navigator.pushReplacementNamed(context, InitialSuggestionsScreen.route);
          } else {
            Navigator.pushReplacementNamed(context, BiomarkerInputScreen.route);
          }
        });
        return const Scaffold(body: SizedBox.shrink());
      },
    );
  }
}
