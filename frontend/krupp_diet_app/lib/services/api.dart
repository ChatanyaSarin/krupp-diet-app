import 'dart:convert';
import 'package:http/http.dart' as http;

/// Change this one line when you deploy
const String _baseUrl = 'http://localhost:8000';   // ← Flask dev server
// For Android emulator use: 'http://10.0.2.2:8000'

class ApiService {
  static Future<void> setupUser({
    required String username,
    required int heightFt,
    required int heightIn,
    required int weight,
    required String goals,
    required String restrictions,
  }) async {
    final uri = Uri.parse('$_baseUrl/setup_user');
    final body = {
      "Username": username,
      "Height": heightFt * 12 + heightIn,
      "Weight": weight,
      "Goals": goals,
      "DietaryRestrictions": restrictions,
    };

    final res =
        await http.post(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode(body));

    if (res.statusCode != 201) {
      throw Exception('API error ${res.statusCode}: ${res.body}');
    }
  }

  static Future<Map<String, dynamic>> generateInitialMeals(String username) async {
    final uri = Uri.parse('$_baseUrl/meals/initial');
    final res = await http.post(uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"Username": username}));

    if (res.statusCode != 200) throw Exception('API error ${res.statusCode}');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  // …repeat for /meals/feedback, /biomarkers, /meals/daily, /summaries
}
