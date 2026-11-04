import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/cupertino.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

part 'reference_feed.dart';
part 'profile_ml_widgets.dart';

const igBlue = Color(0xFF0095F6);
const igRed = Color(0xFFED4956);
const igGrey = Color(0xFF8E8E8E);
const igBorder = Color(0xFFDBDBDB);
const igFill = Color(0xFFEFEFEF);
const igStoryGradient = LinearGradient(
  begin: Alignment.bottomLeft,
  end: Alignment.topRight,
  colors: [
    Color(0xFFFEDA75),
    Color(0xFFFA7E1E),
    Color(0xFFD62976),
    Color(0xFF962FBF),
    Color(0xFF4F5BD5),
  ],
);

void main() => runApp(const SocialDemoApp());

class SocialDemoApp extends StatelessWidget {
  const SocialDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Instagram · Impersonation concept',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Arial',
        splashFactory: NoSplash.splashFactory,
        scaffoldBackgroundColor: Colors.white,
        colorScheme: const ColorScheme.light(
          primary: igBlue,
          surface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
          elevation: 0,
          scrolledUnderElevation: 0,
          surfaceTintColor: Colors.transparent,
        ),
        iconTheme: const IconThemeData(color: Colors.black),
        iconButtonTheme: IconButtonThemeData(
          style: IconButton.styleFrom(foregroundColor: Colors.black),
        ),
        dividerColor: igBorder,
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: const BorderSide(color: igBorder),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: igBlue,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ),
      home: const HomeShell(),
    );
  }
}

class Account {
  final String handle;
  final String name;
  final String bio;
  final int posts, followers, following;
  const Account(
    this.handle,
    this.name,
    this.bio,
    this.posts,
    this.followers,
    this.following,
  );

  /// null, 'under_review' or 'confirmed_fake', taken from the Python API.
  String? get flag => switch (statuses.value[handle]) {
    'under_review' => 'under_review',
    'confirmed' => 'confirmed_fake',
    _ => null,
  };
}

const apiBase = 'http://127.0.0.1:8000';

/// Reviewer endpoints need the shared secret: flutter run --dart-define=ADMIN_TOKEN=...
const adminHeaders = {'X-Admin-Token': String.fromEnvironment('ADMIN_TOKEN')};

/// suspect handle -> claim status, refreshed from the Python API.
final statuses = ValueNotifier<Map<String, String>>({});

Future<void> refreshStatuses() async {
  try {
    final resp = await http.get(Uri.parse('$apiBase/statuses'));
    if (resp.statusCode == 200) {
      statuses.value = (jsonDecode(resp.body) as Map<String, dynamic>).map(
        (k, v) => MapEntry(k, v as String),
      );
    }
  } catch (_) {
    // API offline: keep the last known statuses.
  }
}

const accounts = <Account>[
  Account('aigerim.k', 'Aigerim K.', 'Photographer · Astana', 128, 5400, 310),
  Account(
    'aigerim.k_official',
    'Aigerim K.',
    'DM for collab, send money first',
    6,
    40,
    2100,
  ),
  Account('nurzhan.dev', 'Nurzhan', 'Python · AI hackathons', 42, 890, 450),
];

const captions = [
  'Golden hour in the city',
  'Weekend mood',
  'New project is live',
  'Coffee first, everything else later',
];

String fmt(int n) =>
    n.toString().replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => ',');

void openProfile(BuildContext context, Account a) => Navigator.push(
  context,
  MaterialPageRoute(builder: (_) => ProfileScreen(account: a)),
);

/// Square photo from picsum.photos (Unsplash licence). The same seed always
/// gives the same picture. Falls back to the pastel gradient while loading,
/// or if the network is unavailable.
class Photo extends StatelessWidget {
  final String seed;
  final int size;
  final int fallbackIndex;
  const Photo(this.seed, this.size, this.fallbackIndex, {super.key});

  @override
  Widget build(BuildContext context) {
    final placeholder = DecoratedBox(
      decoration: BoxDecoration(gradient: pastel(fallbackIndex)),
    );
    return Image.network(
      'https://picsum.photos/seed/${Uri.encodeComponent(seed)}/$size/$size',
      fit: BoxFit.cover,
      loadingBuilder: (_, child, progress) =>
          progress == null ? child : placeholder,
      errorBuilder: (_, _, _) => placeholder,
    );
  }
}

LinearGradient pastel(int i) => LinearGradient(
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
  colors: [
    Colors.primaries[i % Colors.primaries.length].shade100,
    Colors.primaries[(i + 5) % Colors.primaries.length].shade200,
  ],
);

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});
  @override
  State<HomeShell> createState() => _HomeShellState();
}

void showAccountActions(
  BuildContext context,
  Account account, {
  VoidCallback? onSave,
  bool saved = false,
}) {
  showModalBottomSheet<void>(
    context: context,
    backgroundColor: Colors.white,
    showDragHandle: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
    ),
    builder: (sheetContext) => SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (onSave != null)
            ListTile(
              leading: Icon(
                saved ? CupertinoIcons.bookmark_fill : CupertinoIcons.bookmark,
              ),
              title: Text(saved ? 'Unsave' : 'Save'),
              onTap: () {
                Navigator.pop(sheetContext);
                onSave();
              },
            ),
          ListTile(
            leading: const Icon(CupertinoIcons.person),
            title: const Text('About this account'),
            onTap: () {
              Navigator.pop(sheetContext);
              openProfile(context, account);
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(
              CupertinoIcons.exclamationmark_shield,
              color: igRed,
            ),
            title: const Text(
              'Report impersonation',
              style: TextStyle(color: igRed, fontWeight: FontWeight.w600),
            ),
            subtitle: const Text('Someone is pretending to be you'),
            onTap: () {
              Navigator.pop(sheetContext);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ReportFakePage(suspect: account),
                ),
              );
            },
          ),
          ListTile(
            leading: const Icon(CupertinoIcons.checkmark_shield),
            title: const Text('Review reports'),
            onTap: () {
              Navigator.pop(sheetContext);
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => Scaffold(
                    appBar: AppBar(title: const Text('Review reports')),
                    body: const ReviewPage(),
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 12),
        ],
      ),
    ),
  );
}

/// Round avatar with the gradient story ring.
class StoryAvatar extends StatelessWidget {
  final String text;
  final double size;
  final bool ring;
  const StoryAvatar(this.text, {super.key, this.size = 32, this.ring = true});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(ring ? 2 : 0),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: ring ? igStoryGradient : null,
      ),
      child: Container(
        padding: EdgeInsets.all(ring ? 2 : 0),
        decoration: const BoxDecoration(
          shape: BoxShape.circle,
          color: Colors.white,
        ),
        child: ClipOval(
          child: SizedBox(
            width: size,
            height: size,
            child: Image.asset(
              'assets/avatars/${text.startsWith('A') || text.startsWith('a')
                  ? 'aigerim'
                  : text.startsWith('N') || text.startsWith('n') || text.startsWith('Y')
                  ? 'nurzhan'
                  : 'friend'}.jpg',
              fit: BoxFit.cover,
              errorBuilder: (_, error, trace) => ColoredBox(
                color: igFill,
                child: Center(
                  child: Text(text.isEmpty ? '?' : text[0].toUpperCase()),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class FlagBadge extends StatelessWidget {
  final String flag;
  const FlagBadge(this.flag, {super.key});
  @override
  Widget build(BuildContext context) {
    final confirmed = flag == 'confirmed_fake';
    final color = confirmed ? igRed : const Color(0xFFB8860B);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            confirmed ? Icons.gpp_bad : Icons.hourglass_top,
            size: 12,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            confirmed ? 'Confirmed impersonation' : 'Report under review',
            style: TextStyle(
              fontSize: 11,
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class SearchPage extends StatefulWidget {
  const SearchPage({super.key});
  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  String q = '';
  @override
  Widget build(BuildContext context) => ValueListenableBuilder(
    valueListenable: statuses,
    builder: (_, value, child) => _buildSearch(context),
  );

  Widget _buildSearch(BuildContext context) {
    final hits = const [referenceAccount, ...accounts]
        .where((a) => a.handle.contains(q.toLowerCase().replaceAll('@', '')))
        .toList();
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: TextField(
            decoration: InputDecoration(
              prefixIcon: const Icon(Icons.search, color: igGrey),
              hintText: 'Search',
              filled: true,
              fillColor: igFill,
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(vertical: 10),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: BorderSide.none,
              ),
            ),
            onChanged: (v) => setState(() => q = v),
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.only(bottom: 16),
            children: [
              for (final a in hits)
                InkWell(
                  onTap: () => openProfile(context, a),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    child: Row(
                      children: [
                        StoryAvatar(a.name, size: 44),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                a.handle,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              Text(
                                a.name,
                                style: const TextStyle(color: igGrey),
                              ),
                              if (a.flag != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 2),
                                  child: FlagBadge(a.flag!),
                                ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class ProfileScreen extends StatelessWidget {
  final Account account;
  const ProfileScreen({super.key, required this.account});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(
        account.handle,
        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
      ),
    ),
    body: ValueListenableBuilder(
      valueListenable: statuses,
      builder: (_, _, _) => ProfilePage(account: account),
    ),
  );
}

class ProfilePage extends StatelessWidget {
  final Account account;
  final bool showHandleBar;
  const ProfilePage({
    super.key,
    required this.account,
    this.showHandleBar = false,
  });

  Widget _stat(String n, String l) => Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      Text(
        n,
        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 17),
      ),
      Text(l, style: const TextStyle(fontSize: 13)),
    ],
  );

  Widget _btn(
    String text,
    VoidCallback onTap, {
    Color bg = igFill,
    Color fg = Colors.black,
  }) {
    return Expanded(
      child: FilledButton(
        style: FilledButton.styleFrom(
          minimumSize: const Size(0, 34),
          padding: EdgeInsets.zero,
          backgroundColor: bg,
          foregroundColor: fg,
        ),
        onPressed: onTap,
        child: Text(text, style: const TextStyle(fontWeight: FontWeight.w600)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final flag = account.flag;
    return ListView(
      padding: const EdgeInsets.only(bottom: 16),
      children: [
        if (showHandleBar)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
            child: Row(
              children: [
                Text(
                  account.handle,
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 20,
                  ),
                ),
                const Icon(Icons.keyboard_arrow_down),
                const Spacer(),
                IconButton(
                  tooltip: 'Profile menu',
                  icon: const Icon(CupertinoIcons.line_horizontal_3),
                  onPressed: () => showAccountActions(context, account),
                ),
              ],
            ),
          ),
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              StoryAvatar(account.name, size: 80),
              const SizedBox(width: 12),
              Expanded(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    Expanded(child: _stat(fmt(account.posts), 'posts')),
                    Expanded(child: _stat(fmt(account.followers), 'followers')),
                    Expanded(child: _stat(fmt(account.following), 'following')),
                  ],
                ),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                account.name,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              Text(account.bio),
              if (flag != null)
                Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: FlagBadge(flag),
                ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
          child: Row(
            children: [
              _btn('Follow', () {}, bg: igBlue, fg: Colors.white),
              const SizedBox(width: 6),
              _btn('Message', () {}),
              const SizedBox(width: 6),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
          child: OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.black,
              side: const BorderSide(color: igBorder),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            icon: const Icon(CupertinoIcons.exclamationmark_shield, size: 17),
            label: const Text('Report impersonation'),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ReportFakePage(suspect: account),
              ),
            ),
          ),
        ),
        SizedBox(
          height: 92,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            children: [
              for (final t in ['Work', 'Travel', 'Friends'])
                Padding(
                  padding: const EdgeInsets.only(right: 16),
                  child: Column(
                    children: [
                      Container(
                        width: 62,
                        height: 62,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(color: igBorder),
                          color: igFill,
                        ),
                        child: ClipOval(
                          child: Photo('highlight-$t', 160, t.length),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(t, style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
            ],
          ),
        ),
        const Divider(height: 1),
        Row(
          children: [
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: const BoxDecoration(
                  border: Border(
                    bottom: BorderSide(color: Colors.black, width: 1.5),
                  ),
                ),
                child: const Icon(Icons.grid_on, size: 24),
              ),
            ),
            const Expanded(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 10),
                child: Icon(Icons.person_pin_outlined, size: 26, color: igGrey),
              ),
            ),
          ],
        ),
        GridView.count(
          crossAxisCount: 3,
          childAspectRatio: 0.8,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 1.5,
          crossAxisSpacing: 1.5,
          children: [
            for (var i = 0; i < 9; i++)
              Photo('grid-${account.handle}-$i', 400, i * 2),
          ],
        ),
      ],
    );
  }
}

/// Reviewer screen: confirm or reject claims that are under review.
class AnalysisSummary extends StatelessWidget {
  final Map<String, dynamic> analysis;
  const AnalysisSummary({super.key, required this.analysis});

  @override
  Widget build(BuildContext context) {
    final provider = analysis['provider'];
    final title = provider == 'meta'
        ? 'Meta AI · ${analysis['model'] ?? 'Muse Spark'}'
        : provider == 'local'
        ? 'Screenshot comparison · local'
        : provider == 'mock'
        ? 'Simulated analysis'
        : 'Earlier comparison';
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: igBorder),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(CupertinoIcons.checkmark_shield, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          if (analysis['summary'] is String) ...[
            const SizedBox(height: 8),
            Text(analysis['summary'] as String),
          ],
          for (final section in const {
            'evidence': 'Evidence',
            'differences': 'Differences',
            'limitations': 'Limitations',
          }.entries)
            if (analysis[section.key] is List &&
                (analysis[section.key] as List).isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                section.value,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              for (final line in analysis[section.key] as List) Text('• $line'),
            ],
          const SizedBox(height: 8),
          const Text(
            'Similarity is not proof of impersonation. A reviewer makes the final decision.',
            style: TextStyle(color: igGrey, fontSize: 12),
          ),
          if (analysis['profile_ml'] is Map<String, dynamic>)
            ProfileMLSummary(
              result: analysis['profile_ml'] as Map<String, dynamic>,
            ),
        ],
      ),
    );
  }
}

class ReviewPage extends StatefulWidget {
  const ReviewPage({super.key});
  @override
  State<ReviewPage> createState() => _ReviewPageState();
}

class _ReviewPageState extends State<ReviewPage> {
  List<Map<String, dynamic>> claims = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final resp = await http.get(
        Uri.parse('$apiBase/claims/pending'),
        headers: adminHeaders,
      );
      if (resp.statusCode != 200) {
        if (mounted) {
          setState(() {
            loading = false;
            error = resp.statusCode == 503
                ? 'Reviewer access is not configured. Set ADMIN_TOKEN on the server and rebuild with the same token.'
                : 'Reviewer access denied. Check your reviewer token.';
          });
        }
        return;
      }
      claims = (jsonDecode(resp.body) as List).cast<Map<String, dynamic>>();
    } catch (_) {
      error = 'Cannot reach the server. Is the Python API running?';
    }
    if (mounted) setState(() => loading = false);
  }

  Future<void> _decide(String id, String status) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBase/claims/$id/status?status=$status'),
        headers: adminHeaders,
      );
      if (response.statusCode != 200) {
        if (mounted) {
          setState(
            () => error = 'Decision was not saved. Check reviewer access.',
          );
        }
        return;
      }
    } catch (_) {
      if (mounted) setState(() => error = 'Could not save the decision.');
      return;
    }
    await refreshStatuses();
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.fromLTRB(12, 12, 12, 100),
        children: [
          Text(
            'Claims under review (${claims.length})',
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(error!),
            ),
          if (claims.isEmpty && error == null)
            const Padding(
              padding: EdgeInsets.only(top: 24),
              child: Center(child: Text('Nothing to review.')),
            ),
          for (final c in claims)
            Card(
              margin: const EdgeInsets.only(top: 12),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '@${c['owner_handle']} reports @${c['suspect_handle']}',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 4),
                    Text('Similarity: ${((c['score'] as num) * 100).round()}%'),
                    const SizedBox(height: 4),
                    for (final r in (c['reasons'] as List)) Text('• $r'),
                    AnalysisSummary(
                      analysis: (c['analysis'] as Map<String, dynamic>?) ?? {},
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        FilledButton(
                          onPressed: () =>
                              _decide(c['id'] as String, 'confirmed'),
                          child: const Text('Confirm fake'),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton(
                          onPressed: () =>
                              _decide(c['id'] as String, 'rejected'),
                          child: const Text('Reject'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class ReportFakePage extends StatefulWidget {
  final Account suspect;
  const ReportFakePage({super.key, required this.suspect});
  @override
  State<ReportFakePage> createState() => _ReportFakePageState();
}

class _ReportFakePageState extends State<ReportFakePage> {
  final owner = TextEditingController();
  PlatformFile? originalImg;
  PlatformFile? suspectImg;
  String? result;
  bool loading = false;
  Map<String, dynamic>? serviceStatus;
  Map<String, dynamic>? analysisResult;
  bool includeProfileML = false;
  final profileFactsKey = GlobalKey<ProfileFactsFieldsState>();

  @override
  void initState() {
    super.initState();
    _loadServiceStatus();
  }

  Future<void> _loadServiceStatus() async {
    try {
      final response = await http
          .get(Uri.parse('$apiBase/analysis/status'))
          .timeout(const Duration(seconds: 5));
      if (response.statusCode == 200 && mounted) {
        setState(() {
          serviceStatus = jsonDecode(response.body) as Map<String, dynamic>;
          includeProfileML =
              (serviceStatus!['profile_ml']
                  as Map<String, dynamic>?)?['ready'] ==
              true;
        });
      }
    } catch (_) {
      // Submission will show an actionable error if the API is unavailable.
    }
  }

  @override
  void dispose() {
    owner.dispose();
    super.dispose();
  }

  Future<PlatformFile?> _pick() => FilePicker.pickFile(type: FileType.image);

  Future<void> _submit() async {
    if (owner.text.trim().isEmpty ||
        originalImg == null ||
        suspectImg == null) {
      setState(() => result = 'Enter your handle and attach both screenshots.');
      return;
    }
    Map<String, dynamic>? facts;
    if (includeProfileML) {
      try {
        facts = profileFactsKey.currentState!.facts();
      } on FormatException {
        setState(() => result = 'Check the profile facts before submitting.');
        return;
      }
    }
    setState(() {
      loading = true;
      result = null;
      analysisResult = null;
    });
    try {
      final origBytes = await originalImg!.readAsBytes();
      final suspBytes = await suspectImg!.readAsBytes();
      final req = http.MultipartRequest('POST', Uri.parse('$apiBase/claims'))
        ..fields['owner'] = owner.text.trim()
        ..fields['suspect'] = widget.suspect.handle
        ..files.add(
          http.MultipartFile.fromBytes(
            'original',
            origBytes,
            filename: originalImg!.name,
          ),
        )
        ..files.add(
          http.MultipartFile.fromBytes(
            'suspect_image',
            suspBytes,
            filename: suspectImg!.name,
          ),
        );
      if (facts != null) req.fields['profile_facts'] = jsonEncode(facts);
      final resp = await http.Response.fromStream(await req.send());
      if (!mounted) return;
      final body = jsonDecode(resp.body) as Map<String, dynamic>;
      if (resp.statusCode != 200) {
        setState(() => result = 'Error: ${body['detail'] ?? resp.statusCode}');
      } else {
        await refreshStatuses();
        if (!mounted) return;
        analysisResult = (body['analysis'] as Map<String, dynamic>?) ?? {};
        final reasons = (body['reasons'] as List).map((r) => '• $r').join('\n');
        setState(
          () => result =
              'Claim ${body['id']} submitted.\nSimilarity: '
              '${((body['score'] as num) * 100).round()}%\n'
              'Status: ${body['status']}\n$reasons',
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(
        () => result = 'Cannot reach the server. Is the Python API running?',
      );
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Report @${widget.suspect.handle}')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                color: igFill,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                serviceStatus == null
                    ? 'The analysis source is shown with your result.'
                    : serviceStatus!['provider'] == 'meta'
                    ? serviceStatus!['ready'] == true
                          ? 'Meta AI · ${serviceStatus!['model']}. Your two screenshots will be sent to Meta for analysis.'
                          : 'Meta AI is not configured. Add META_API_KEY to the server and restart the API.'
                    : 'Screenshot analysis: local comparison. Meta AI is not connected.',
              ),
            ),
            const Text(
              'Are you the original account owner? Submit your handle and '
              'proof. We compare the evidence. A reviewer checks your report before any label is shown.',
            ),
            const SizedBox(height: 16),
            TextField(
              controller: owner,
              decoration: const InputDecoration(
                labelText: 'Your original handle',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              icon: const Icon(Icons.upload_file),
              label: Text(originalImg?.name ?? 'Your profile screenshot'),
              onPressed: () async {
                final f = await _pick();
                if (f != null) setState(() => originalImg = f);
              },
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              icon: const Icon(Icons.upload_file),
              label: Text(suspectImg?.name ?? 'Suspected fake screenshot'),
              onPressed: () async {
                final f = await _pick();
                if (f != null) setState(() => suspectImg = f);
              },
            ),
            if ((serviceStatus?['profile_ml']
                    as Map<String, dynamic>?)?['ready'] ==
                true) ...[
              SwitchListTile.adaptive(
                contentPadding: EdgeInsets.zero,
                title: const Text('Add ML profile check'),
                subtitle: const Text(
                  'An independent risk signal from profile facts',
                ),
                value: includeProfileML,
                onChanged: loading
                    ? null
                    : (value) => setState(() => includeProfileML = value),
              ),
              if (includeProfileML)
                ProfileFactsFields(
                  key: profileFactsKey,
                  account: widget.suspect,
                ),
            ],
            const SizedBox(height: 12),
            FilledButton(
              onPressed: loading || serviceStatus?['ready'] == false
                  ? null
                  : _submit,
              child: Text(loading ? 'Checking...' : 'Submit claim'),
            ),
            if (result != null)
              Padding(
                padding: const EdgeInsets.only(top: 16),
                child: Text(result!),
              ),
            if (analysisResult != null)
              AnalysisSummary(analysis: analysisResult!),
          ],
        ),
      ),
    );
  }
}
