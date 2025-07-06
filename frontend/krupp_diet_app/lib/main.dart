import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/api.dart';

String currentUsername = 'demo_user';

void main() => runApp(const DietApp());

class DietApp extends StatelessWidget {
  const DietApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Krupp Diet App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF008060),
        useMaterial3: true,
      ),
      initialRoute: SetupScreen.route,
      routes: {
        SetupScreen.route: (_) => const SetupScreen(),
        InitialSuggestionsScreen.route: (_) => const InitialSuggestionsScreen(),
        BiomarkerInputScreen.route: (_) => const BiomarkerInputScreen(),
        DailySuggestionsScreen.route: (_) => const DailySuggestionsScreen(),
      },
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                               SET-UP PAGE                                 */
/* -------------------------------------------------------------------------- */
class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});
  static const route = '/setup';

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameCtrl = TextEditingController();
  final _feetCtrl = TextEditingController();
  final _inchesCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();
  final _goalsCtrl = TextEditingController();
  final _restrictionsCtrl = TextEditingController();

  @override
  void dispose() {
    _usernameCtrl.dispose();  
    _feetCtrl.dispose();
    _inchesCtrl.dispose();
    _weightCtrl.dispose();
    _goalsCtrl.dispose();
    _restrictionsCtrl.dispose();
    super.dispose();
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;

    currentUsername = _usernameCtrl.text.trim();
    await ApiService.setupUser(
      username: currentUsername,
      heightInches: int.parse(_feetCtrl.text) * 12 + int.parse(_inchesCtrl.text),
      weight: int.parse(_weightCtrl.text),
      goals: _goalsCtrl.text,
      restrictions: _restrictionsCtrl.text,
    );

    Navigator.pushNamed(context, InitialSuggestionsScreen.route);
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome to the Krupp Diet App')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Input the following to get started', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              _labelledField(label: 'Username:', controller: _usernameCtrl, hint: 'e.g. alice'), // NEW
              const SizedBox(height: 16),
              _heightInputs(),
              const SizedBox(height: 16),
              _labelledField(
                label: 'Weight:',
                controller: _weightCtrl,
                hint: 'e.g. 150',
                suffix: 'lbs',
                isNumber: true,
              ),
              const SizedBox(height: 16),
              _labelledField(
                label: 'Goals:',
                controller: _goalsCtrl,
                hint: 'bulk, cut, more energy',
              ),
              const SizedBox(height: 16),
              _labelledField(
                label: 'Dietary Restrictions:',
                controller: _restrictionsCtrl,
                hint: 'vegetarian, gluten-free',
              ),
              const SizedBox(height: 32),
              Row(
                children: [
                  const Spacer(),
                  ElevatedButton(onPressed: _submit, child: const Text('Next')),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _heightInputs() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Height:', style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _numberField(
                controller: _feetCtrl,
                hint: 'ft',
                suffix: 'ft',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _numberField(
                controller: _inchesCtrl,
                hint: 'in',
                suffix: 'in',
              ),
            ),
          ],
        ),
      ],
    );
  }

  /* --------------------------- helper widgets --------------------------- */
  Widget _numberField({
    required TextEditingController controller,
    String? hint,
    String? suffix,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        hintText: hint,
        suffixText: suffix,
        border: const OutlineInputBorder(),
      ),
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
      validator: (v) {
        if (v == null || v.isEmpty) return 'Required';
        if (int.tryParse(v) == null) return 'Enter a number';
        return null;
      },
    );
  }

  Widget _labelledField({
    required String label,
    required TextEditingController controller,
    String? hint,
    String? suffix,
    bool isNumber = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          decoration: InputDecoration(
            hintText: hint,
            suffixText: suffix,
            border: const OutlineInputBorder(),
          ),
          keyboardType: isNumber ? TextInputType.number : TextInputType.text,
          inputFormatters: isNumber
              ? [FilteringTextInputFormatter.digitsOnly]
              : null,
          validator: (v) {
            if (v == null || v.isEmpty) return 'Required';
            if (isNumber && int.tryParse(v) == null) return 'Enter a number';
            return null;
          },
        ),
      ],
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                    INITIAL MEAL SUGGESTIONS  (10 cards)                    */
/* -------------------------------------------------------------------------- */
class InitialSuggestionsScreen extends StatefulWidget {
  const InitialSuggestionsScreen({super.key});
  static const route = '/initial-suggestions';

  @override
  State<InitialSuggestionsScreen> createState() => _InitialSuggestionsScreenState();
}

class _InitialSuggestionsScreenState extends State<InitialSuggestionsScreen> {
  late Future<Map<String, dynamic>> _mealsFut;

  @override
  void initState() {
    super.initState();
    _mealsFut = ApiService.fetchInitialMeals(currentUsername);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Initial Suggested Meals')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _mealsFut,
        builder: (ctx, snap) {
          if (!snap.hasData) return const Center(child: CircularProgressIndicator());
          final meals = snap.data!;
          final keys = meals.keys.toList();
          return Padding(
            padding: const EdgeInsets.all(16),
            child: GridView.builder(
              itemCount: keys.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2, crossAxisSpacing: 16, mainAxisSpacing: 16, childAspectRatio: .8),
              itemBuilder: (_, idx) => MealCard(
                title: meals[keys[idx]]['long_name'],
                mealCode: keys[idx],   // pass down so MealCard can call likeMeal()
              ),
            ),
          );
        },
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                       DAILY BIOMARKER INPUT  (0-10)                        */
/* -------------------------------------------------------------------------- */
class BiomarkerInputScreen extends StatefulWidget {
  const BiomarkerInputScreen({super.key});
  static const route = '/biomarker-input';

  @override
  State<BiomarkerInputScreen> createState() => _BiomarkerInputScreenState();
}

class _BiomarkerInputScreenState extends State<BiomarkerInputScreen> {
  final _ctrls = List.generate(4, (_) => TextEditingController());

  bool _validateRange() => _ctrls.every((c) {
    final v = int.tryParse(c.text);
    return v != null && v >= 0 && v <= 10;
  });

  void _continue() async {
    if (!_validateRange()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Each biomarker must be an integer 0–10')),
      );
      return;
    }
    await ApiService.sendBiomarkers(
      username: currentUsername,
      b1: int.parse(_ctrls[0].text),
      b2: int.parse(_ctrls[1].text),
      b3: int.parse(_ctrls[2].text),
    );
    Navigator.pushNamed(context, DailySuggestionsScreen.route);
  }

  @override
  void dispose() {
    for (final c in _ctrls) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('How Are You Feeling?')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (int i = 0; i < 4; i++) ...[
              Text(
                'Biomarker ${i + 1}:',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _ctrls[i],
                decoration: const InputDecoration(
                  hintText: '0-10',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(2),
                ],
              ),
              const SizedBox(height: 16),
            ],
            const Spacer(),
            Row(
              children: [
                const Spacer(),
                ElevatedButton(onPressed: _continue, child: const Text('Next')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                 DAILY MEAL SUGGESTIONS (5 per meal type)                   */
/* -------------------------------------------------------------------------- */
class DailySuggestionsScreen extends StatefulWidget {
  const DailySuggestionsScreen({super.key});
  static const route = '/daily-suggestions';

  @override
  State<DailySuggestionsScreen> createState() => _DailySuggestionsScreenState();
}

class _DailySuggestionsScreenState extends State<DailySuggestionsScreen> {
  late Future<Map<String, dynamic>> _futureDaily;

  @override
  void initState() {
    super.initState();
    _futureDaily = ApiService.fetchDailyMeals(currentUsername);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _futureDaily,
      builder: (ctx, snap) {
        if (!snap.hasData) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        final daily = snap.data!;
        return DefaultTabController(
          length: 3,
          child: Scaffold(
            appBar: AppBar(
              title: const Text('Daily Suggested Meals'),
              bottom: const TabBar(
                tabs: [
                  Tab(text: 'Breakfast'),
                  Tab(text: 'Lunch'),
                  Tab(text: 'Dinner'),
                ],
              ),
            ),
            body: TabBarView(children: [
              _buildMealList('breakfast', daily['breakfast']),
              _buildMealList('lunch', daily['lunch']),
              _buildMealList('dinner', daily['dinner']),
            ]),
          ),
        );
      },
    );
  }

  Widget _buildMealList(String type, Map<String, dynamic> meals) {
    final slugs = meals.keys.toList();
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: slugs.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, i) => MealCard(
        title: meals[slugs[i]]['long_name'],
        mealCode: slugs[i],
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                             MEAL CARD WIDGET                               */
/* -------------------------------------------------------------------------- */
class MealCard extends StatefulWidget {
  const MealCard({
    super.key,
    required this.title,
    required this.mealCode,   // ← NEW
  });
  final String title;
  final String mealCode;      // ← NEW

  @override
  State<MealCard> createState() => _MealCardState();
}

class _MealCardState extends State<MealCard> {
  bool? liked; // null = undecided

  @override
  Widget build(BuildContext context) {
    String lorem(int w) => List.filled(w, 'lorem').join(' ') + '.';

    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(widget.title, style: Theme.of(context).textTheme.titleMedium),
            const Divider(),
            const Text('Ingredients:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text('• ' + lorem(6)),
            const SizedBox(height: 8),
            const Text('Steps:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(lorem(18)),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _fbBtn('Like', true, Colors.green),
                _fbBtn('Dislike', false, Colors.red),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _fbBtn(String label, bool value, Color color) {
    final selected = liked == value;
    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        backgroundColor: selected ? color : null,
        foregroundColor: selected ? Colors.white : Colors.black,
        minimumSize: const Size(72, 36),
      ),
      onPressed: () async {
        setState(() => liked = value);
        try {
          await ApiService.likeMeal(
            username: currentUsername,
            mealCode: widget.mealCode,
            like: value,
          );
        } catch (e) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed: $e')),
          );
        }
      },
      child: Text(label),
    );
  }
}


/* -------------------------------------------------------------------------- */
/*                             MEAL LIST WIDGET                               */
/* -------------------------------------------------------------------------- */
class MealList extends StatelessWidget {
  const MealList({super.key, required this.mealType});
  final String mealType;

  @override
  Widget build(BuildContext context) {
    final meals = List.generate(5, (i) => '$mealType Meal ${i + 1}');
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: meals.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, idx) => MealCard(title: meals[idx], mealCode: meals[idx]),
    );
  }
}

