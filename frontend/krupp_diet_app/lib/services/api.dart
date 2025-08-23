import 'dart:convert';
import 'package:http/http.dart' as http;

/// Flip this when you deploy (Android emulator ⇒ 10.0.2.2)
const String _host = '127.0.0.1';
const int _port = 8000;
Uri _u(String path) => Uri(scheme: 'http', host: _host, port: _port, path: path);

class ApiService {
  // ---------- AUTH ----------
  static Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    final res = await http.post(_u('/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}));
    if (res.statusCode == 200) return jsonDecode(res.body);
    if (res.statusCode == 409) {
      // server can return 409 to mean "user exists but no password set yet"
      return {'needsPassword': true};
    }
    throw Exception('Login failed: ${res.statusCode} ${res.body}');
  }

  static Future<void> setPassword({
    required String username,
    required String password,
  }) async {
    final res = await http.post(_u('/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}));
    if (res.statusCode != 201) {
      throw Exception('Set password failed: ${res.statusCode} ${res.body}');
    }
  }

  // ---------- STATUS ----------
  static Future<Map<String, dynamic>> getUserStatus(String username) async {
    final res = await http.get(_u('user/status?username=$username'));
    if (res.statusCode != 200) {
      throw Exception('Status failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  // ---------- EXISTING METHODS (keep yours) ----------
  
  
static Future<void> setupUser({
    required String username,
    required int heightInches,
    required int weight,
    required String goals,
    required String restrictions,
  }) async { 
    final res = await http.post(
    _u('/setup_user'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'Username': username,
      'Height': heightInches,
      'Weight': weight,
      'Goals': goals,
      'DietaryRestrictions': restrictions,
    }),
  );
  if (res.statusCode != 201) {
    throw Exception('setup_user failed: ${res.statusCode} ${res.body}');
  }
  }

  static Future<Map<String, dynamic>> fetchInitialMeals(String username) async {
    final res = await http.post(_u('/meals/initial'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'Username': username}));
    if (res.statusCode != 200) {
      throw Exception('meals/initial failed: ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<void> sendBiomarkers({
    required String username,
    required int b1,
    required int b2,
    required int b3,
  }) async { /* unchanged */ }

  static Future<Map<String, dynamic>> fetchDailyMeals(String username) async {
    final res = await http.post(_u('/meals/daily'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'Username': username}));
    if (res.statusCode != 200) {
      throw Exception('meals/daily failed: ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  // Add initial flag
  static Future<void> likeMeal({
    required String username,
    required String mealCode,
    required bool like,
    required bool initial,         // NEW
  }) async {
    final res = await http.post(_u('/meals/feedback'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'Username': username,
          'MealCode': mealCode,
          'Like': like,
          'Initial': initial,      // server writes this into UserMealPreferences.Initial
        }));
    if (res.statusCode != 201) {
      throw Exception('feedback failed: ${res.statusCode} ${res.body}');
    }
  }
}
