import 'dart:convert';
import 'package:http/http.dart' as http;

/// Flip this when you deploy (Android emulator ⇒ 10.0.2.2)
const String _baseUrl = 'http://localhost:8000';

class ApiService {
  /*--------------------------- USER SET-UP ---------------------------*/
  static Future<void> setupUser({
    required String username,
    required int heightInches,
    required int weight,
    required String goals,
    required String restrictions,
  }) async {
    final uri = Uri.parse('$_baseUrl/setup_user');
    final res = await http.post(
      uri,
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
      throw Exception('setup_user failed: ${res.body}');
    }
  }

  /*---------------------- INITIAL MEAL GENERATION --------------------*/
  static Future<Map<String, dynamic>> fetchInitialMeals(String username) async {
    final uri = Uri.parse('$_baseUrl/meals/initial');
    final res = await http.post(uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'Username': username}));
    if (res.statusCode != 200) {
      throw Exception('meals/initial failed: ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  /*------------------------- BIOMARKER WRITE -------------------------*/
  static Future<void> sendBiomarkers({
    required String username,
    required int b1,
    required int b2,
    required int b3,
  }) async {
    final uri = Uri.parse('$_baseUrl/biomarkers');
    final res = await http.post(uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'Username': username,
          'BIOMARKER 1': b1,
          'BIOMARKER 2': b2,
          'BIOMARKER 3': b3,
        }));
    if (res.statusCode != 201) {
      throw Exception('biomarkers failed: ${res.body}');
    }
  }

  /*------------------------- DAILY MEALS -----------------------------*/
  static Future<Map<String, dynamic>> fetchDailyMeals(String username) async {
    final uri = Uri.parse('$_baseUrl/meals/daily');
    final res = await http.post(uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'Username': username}));
    if (res.statusCode != 200) {
      throw Exception('meals/daily failed: ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  /*------------------- LIKE / DISLIKE FEEDBACK -----------------------*/
  static Future<void> likeMeal({
    required String username,
    required String mealCode,
    required bool like,
  }) async {
    final uri = Uri.parse('$_baseUrl/meals/feedback');
    await http.post(uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'Username': username,
          'MealCode': mealCode,
          'Like': like,
        }));
  }
}