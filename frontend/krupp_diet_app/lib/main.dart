import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

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

  final _feetCtrl = TextEditingController();
  final _inchesCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();
  final _goalsCtrl = TextEditingController();
  final _restrictionsCtrl = TextEditingController();

  @override
  void dispose() {
    _feetCtrl.dispose();
    _inchesCtrl.dispose();
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
      appBar: AppBar(
        title: const Text('Welcome to the Krupp Diet App'),
        leading: Navigator.canPop(context) ? const BackButton() : null,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Input the following to get started', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              Text('Height:', style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 8),
              Row(children: [
                Expanded(child: _numberField(controller: _feetCtrl, hint: 'ft', suffix: 'ft')),
                const SizedBox(width: 12),
                Expanded(child: _numberField(controller: _inchesCtrl, hint: 'in', suffix: 'in')),
              ]),
              const SizedBox(height: 16),
              _labelledField(label: 'Weight (lbs):', controller: _weightCtrl, hint: 'e.g. 150', suffix: 'lbs', isNumber: true),
              const SizedBox(height: 16),
              _labelledField(label: 'Goals:', controller: _goalsCtrl, hint: 'bulk, cut, more energy'),
              const SizedBox(height: 16),
              _labelledField(label: 'Dietary Restrictions:', controller: _restrictionsCtrl, hint: 'vegetarian, gluten‑free'),
              const SizedBox(height: 32),
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

  /* ------------------------------- widgets -------------------------------- */

  Widget _numberField({required TextEditingController controller, String? hint, String? suffix}) {
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
          inputFormatters: isNumber ? [FilteringTextInputFormatter.digitsOnly] : null,
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
/*                    INITIAL MEAL SUGGESTIONS (10 meals)                     */
/* -------------------------------------------------------------------------- */
class InitialSuggestionsScreen extends StatelessWidget {
  const InitialSuggestionsScreen({super.key});
  static const route = '/initial-suggestions';

  @override
  Widget build(BuildContext context) {
    final meals = List.generate(10, (i) => 'Meal ${i + 1}');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Initial Suggested Meals'),
        leading: Navigator.canPop(context) ? const BackButton() : null,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: GridView.builder(
          itemCount: meals.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            childAspectRatio: 0.75,
          ),
          itemBuilder: (_, idx) => MealCard(title: meals[idx]),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        icon: const Icon(Icons.arrow_forward),
        label: const Text('Next'),
        onPressed: () => Navigator.pushReplacementNamed(context, BiomarkerInputScreen.route),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                        DAILY BIOMARKER INPUT (ints)                        */
/* -------------------------------------------------------------------------- */
class BiomarkerInputScreen extends StatefulWidget {
  const BiomarkerInputScreen({super.key});
  static const route = '/biomarker-input';

  @override
  State<BiomarkerInputScreen> createState() => _BiomarkerInputScreenState();
}

class _BiomarkerInputScreenState extends State<BiomarkerInputScreen> {
  final List<TextEditingController> _ctrls = List.generate(4, (_) => TextEditingController());

  @override
  void dispose() {
    for (final c in _ctrls) {
      c.dispose();
    }
    super.dispose();
  }

  void _continue() {
    final invalid = _ctrls.any((c) => c.text.isEmpty || int.tryParse(c.text) == null);
    if (invalid) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter numbers for all biomarkers')));
      return;
    }
    Navigator.pushReplacementNamed(context, DailySuggestionsScreen.route);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('How Are You Feeling?'),
        leading: Navigator.canPop(context) ? const BackButton() : null,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (int i = 0; i < 4; i++) ...[
              Text('Biomarker ${i + 1}:', style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 8),
              TextField(
                controller: _ctrls[i],
                decoration: const InputDecoration(
                  hintText: '0‑10',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              ),
              const SizedBox(height: 16),
            ],
            const Spacer(),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton(onPressed: _continue, child: const Text('Next')),
            ),
          ],
        ),
      ),
    );
  }
}

/* -------------------------------------------------------------------------- */
/*                 DAILY SUGGESTIONS PAGE (5 per meal type)                   */
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
          title: const Text('Daily Suggested Meals'),
          leading: Navigator.canPop(context) ? const BackButton() : null,
          bottom: const TabBar(tabs: [
            Tab(text: 'Breakfast'),
            Tab(text: 'Lunch'),
            Tab(text: 'Dinner'),
          ]),
        ),
        body: TabBarView(children: const [
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
  bool? liked; // null = undecided

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.title, style: Theme.of(context).textTheme.titleMedium),
            const Divider(),
            const Text('Ingredients:', style: TextStyle(fontWeight: FontWeight.bold)),
            const Expanded(child: Text('• Lorem ipsum\n• Dolor sit\n• Amet consectetur\n• Adipiscing elit', maxLines: 4, overflow: TextOverflow.ellipsis)),
            const SizedBox(height: 4),
            const Text('Steps:', style: TextStyle(fontWeight: FontWeight.bold)),
            const Expanded(child: Text('1. Lorem ipsum dolor sit amet.\n2. Consectetur adipiscing elit.', maxLines: 4, overflow: TextOverflow.ellipsis)),
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
    return Expanded(
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          backgroundColor: selected ? color : null,
          foregroundColor: selected ? Colors.white : Colors.black,
        ),
        onPressed: () => setState(() => liked = value),
        child: Text(label),
      ),
    );
  }
}

class MealList extends StatelessWidget {
  const MealList({super.key, required this.mealType});
  final String mealType;

  @override
  Widget build(BuildContext context) {
    final meals = List.generate(5, (i) => '$mealType Meal ${i + 1}');
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemCount: meals.length,
      itemBuilder: (_, idx) => SizedBox(height: 220, child: MealCard(title: meals[idx])),
    );
  }
}
