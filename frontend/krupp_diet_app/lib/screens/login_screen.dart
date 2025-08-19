import 'package:flutter/material.dart';
import '../services/api.dart';
import '../main.dart' show currentUsername;
import 'status_gate.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  static const route = '/login';

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _userCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _newPassCtrl = TextEditingController();
  bool _needsPassword = false;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _userCtrl.dispose();
    _passCtrl.dispose();
    _newPassCtrl.dispose();
    super.dispose();
  }

  Future<void> _tryLogin() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _busy = true; _error = null; });
    try {
      final resp = await ApiService.login(
        username: _userCtrl.text.trim(),
        password: _passCtrl.text,
      );
      if (resp['needsPassword'] == true) {
        setState(() { _needsPassword = true; });
      } else {
        currentUsername = _userCtrl.text.trim();
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, StatusGate.route);
      }
    } catch (e) {
      setState(() { _error = e.toString(); });
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _setPassword() async {
    if (_newPassCtrl.text.length < 6) {
      setState(() => _error = 'Password must be at least 6 chars.');
      return;
    }
    setState(() { _busy = true; _error = null; });
    try {
      await ApiService.setPassword(
        username: _userCtrl.text.trim(),
        password: _newPassCtrl.text,
      );
      currentUsername = _userCtrl.text.trim();
      if (!mounted) return;
      Navigator.pushReplacementNamed(context, StatusGate.route);
    } catch (e) {
      setState(() { _error = e.toString(); });
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Card(
            elevation: 4,
            margin: const EdgeInsets.all(24),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Form(
                key: _formKey,
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  Text('Krupp Diet Study', style: theme.textTheme.headlineSmall),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _userCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Username',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) => (v==null || v.isEmpty) ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  if (!_needsPassword) ...[
                    TextFormField(
                      controller: _passCtrl,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Password',
                        border: OutlineInputBorder(),
                      ),
                      validator: (v) => (v==null || v.isEmpty) ? 'Required' : null,
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: _busy ? null : _tryLogin,
                        child: _busy ? const CircularProgressIndicator() : const Text('Log in'),
                      ),
                    ),
                  ] else ...[
                    TextFormField(
                      controller: _newPassCtrl,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Create password',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: _busy ? null : _setPassword,
                        child: _busy ? const CircularProgressIndicator() : const Text('Save password & continue'),
                      ),
                    ),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 8),
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                  ],
                ]),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
