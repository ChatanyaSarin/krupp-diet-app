import 'package:flutter/material.dart';

void main() => runApp(const DietApp());

class DietApp extends StatelessWidget {
  const DietApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Krupp Diet App',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF008060),
        useMaterial3: true,
      ),
      debugShowCheckedModeBanner: false,
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
/*                               SET‑UP PAGE                                 */
/* -------------------------------------------------------------------------- */
class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});
  static const route = '/setup';

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  final _formKey = GlobalKey<FormState>();

  final _heightCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();
  final _goalsCtrl = TextEditingController();
  final _restrictionsCtrl = TextEditingController();

  @override
  void dispose() {
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    _goalsCtrl.dispose();
    _restrictionsCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      Navigator.pushReplacementNamed(context, InitialSuggestionsScreen.route);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome to the Krupp Diet App')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildField(label: 'Height', controller: _heightCtrl),
              const SizedBox(height: 12),
              _buildField(label: 'Weight', controller: _weightCtrl),
              const SizedBox(height: 12),
              _buildField(label: 'Goals', controller: _goalsCtrl),
              const SizedBox(height: 12),
              _buildField(label: 'Dietary Restrictions', controller: _restrictionsCtrl),
              const Spacer(),
              Align(
                alignment: Alignment.centerRight,
                child: ElevatedButton(
                  onPressed: _submit,
                  child: const Text('Next'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildField({required String label, required TextEditingController controller}) {
    return Row(
      children: [
        SizedBox(width: 120, child: Text('$label:')),
        Expanded(
          child: TextFormField(
            controller: controller,
            decoration: const InputDecoration(border: OutlineInputBorder()),
            validator: (v) => v == null || v.isEmpty ? 'Required' : null,
          ),
        ),
      ],
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                         INITIAL MEAL SUGGESTIONS PAGE                      */
/* -------------------------------------------------------------------------- */
class InitialSuggestionsScreen extends StatelessWidget {
  const InitialSuggestionsScreen({super.key});
  static const route = '/initial-suggestions';

  @override
  Widget build(BuildContext context) {
    final meals = List.generate(10, (i) => 'Meal ${i + 1}');

    return Scaffold(
      appBar: AppBar(title: const Text('Suggested Meals')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: GridView.builder(
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 0.75,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
          ),
          itemCount: meals.length,
          itemBuilder: (_, index) => MealCard(title: meals[index]),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushReplacementNamed(context, BiomarkerInputScreen.route),
        label: const Text('Next'),
        icon: const Icon(Icons.arrow_forward),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                        DAILY BIOMARKER INPUT PAGE                          */
/* -------------------------------------------------------------------------- */
class BiomarkerInputScreen extends StatefulWidget {
  const BiomarkerInputScreen({super.key});
  static const route = '/biomarker-input';

  @override
  State<BiomarkerInputScreen> createState() => _BiomarkerInputScreenState();
}

class _BiomarkerInputScreenState extends State<BiomarkerInputScreen> {
  final List<TextEditingController> _controllers = List.generate(4, (_) => TextEditingController());

  @override
  void dispose() {
    for (final c in _controllers) {
      c.dispose();
    }
    super.dispose();
  }

  void _continue() {
    Navigator.pushReplacementNamed(context, DailySuggestionsScreen.route);
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
              Row(
                children: [
                  SizedBox(width: 100, child: Text('Biomarker ${i + 1}:')),
                  Expanded(
                    child: TextField(
                      controller: _controllers[i],
                      decoration: const InputDecoration(border: OutlineInputBorder()),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
            ],
            const Spacer(),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton(
                onPressed: _continue,
                child: const Text('Next'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                         DAILY MEAL SUGGESTIONS PAGE                        */
/* -------------------------------------------------------------------------- */
class DailySuggestionsScreen extends StatelessWidget {
  const DailySuggestionsScreen({super.key});
  static const route = '/daily-suggestions';

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Suggested Meals'),
          bottom: const TabBar(tabs: [
            Tab(text: 'Breakfast'),
            Tab(text: 'Lunch'),
            Tab(text: 'Dinner'),
          ]),
        ),
        body: const TabBarView(children: [
          MealList(mealType: 'Breakfast'),
          MealList(mealType: 'Lunch'),
          MealList(mealType: 'Dinner'),
        ]),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                                 WIDGETS                                    */
/* -------------------------------------------------------------------------- */
class MealCard extends StatefulWidget {
  const MealCard({super.key, required this.title});
  final String title;

  @override
  State<MealCard> createState() => _MealCardState();
}

class _MealCardState extends State<MealCard> {
  bool? liked; // null = undecided, true = like, false = dislike

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            const Text('Ingredients:', style: TextStyle(fontWeight: FontWeight.bold)),
            const Expanded(
              child: SingleChildScrollView(
                child: Text('• Lorem ipsum\n• Dolor sit\n• Amet consectetur\n• Adipiscing elit'),
              ),
            ),
            const SizedBox(height: 8),
            const Text('Steps:', style: TextStyle(fontWeight: FontWeight.bold)),
            const Expanded(
              child: SingleChildScrollView(
                child: Text('1. Lorem ipsum dolor sit amet, consectetur.\n2. Elit sed do eiusmod tempor incididunt ut.'),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _feedbackButton(label: 'Like', isPositive: true),
                _feedbackButton(label: 'Dislike', isPositive: false),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _feedbackButton({required String label, required bool isPositive}) {
    final selected = liked == isPositive;
    return ElevatedButton(
      onPressed: () => setState(() => liked = isPositive),
      style: ElevatedButton.styleFrom(
        backgroundColor: selected
            ? (isPositive ? Colors.green : Colors.red)
            : Colors.grey.shade300,
        foregroundColor: selected ? Colors.white : Colors.black,
      ),
      child: Text(label),
    );
  }
}

class MealList extends StatelessWidget {
  const MealList({super.key, required this.mealType});
  final String mealType;

  @override
  Widget build(BuildContext context) {
    final meals = List.generate(5, (i) => '$mealType Meal ${i + 1}');
    return Padding(
      padding: const EdgeInsets.all(16),
      child: ListView.separated(
        itemCount: meals.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, index) => MealCard(title: meals[index]),
      ),
    );
  }
}
