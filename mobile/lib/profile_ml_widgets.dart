part of 'main.dart';

class ProfileMLSummary extends StatelessWidget {
  final Map<String, dynamic> result;
  const ProfileMLSummary({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final score = result['risk_score'];
    if (score is! num) return const SizedBox.shrink();
    final color = score >= 0.7
        ? igRed
        : score >= 0.3
        ? const Color(0xFF9A6D00)
        : const Color(0xFF24794C);
    final factors = (result['factors'] as List?) ?? [];
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.only(top: 12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Profile ML · logistic regression',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            'ML risk score: ${(score * 100).round()}%',
            style: TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 19,
              color: color,
            ),
          ),
          const SizedBox(height: 8),
          for (final factor in factors)
            Text(
              '• ${factor['label']}: ${factor['value']} (${factor['direction']} the model score)',
            ),
          if (((result['out_of_range_features'] as List?) ?? [])
              .isNotEmpty) ...[
            const SizedBox(height: 8),
            const Text(
              'Some values are outside the training range; this score may be unreliable.',
            ),
          ],
          const SizedBox(height: 8),
          const Text(
            'This detects old fake/spam-like patterns and does not prove impersonation. The score is not a calibrated real-world probability.',
            style: TextStyle(color: igGrey, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

class ProfileFactsFields extends StatefulWidget {
  final Account account;
  const ProfileFactsFields({super.key, required this.account});

  @override
  State<ProfileFactsFields> createState() => ProfileFactsFieldsState();
}

class ProfileFactsFieldsState extends State<ProfileFactsFields> {
  final formKey = GlobalKey<FormState>();
  late final TextEditingController displayName;
  late final TextEditingController bio;
  late final TextEditingController posts;
  late final TextEditingController followers;
  late final TextEditingController following;
  bool hasPhoto = true;
  bool private = false;
  bool externalLink = false;

  @override
  void initState() {
    super.initState();
    displayName = TextEditingController(text: widget.account.name);
    bio = TextEditingController(text: widget.account.bio);
    posts = TextEditingController(text: '${widget.account.posts}');
    followers = TextEditingController(text: '${widget.account.followers}');
    following = TextEditingController(text: '${widget.account.following}');
    externalLink = RegExp(r'https?://|www\.').hasMatch(widget.account.bio);
  }

  @override
  void dispose() {
    for (final controller in [displayName, bio, posts, followers, following]) {
      controller.dispose();
    }
    super.dispose();
  }

  Map<String, dynamic> facts() {
    if (!formKey.currentState!.validate()) {
      throw const FormatException('Invalid profile facts');
    }
    return {
      'handle': widget.account.handle,
      'display_name': displayName.text,
      'bio': bio.text,
      'num_posts': int.parse(posts.text),
      'num_followers': int.parse(followers.text),
      'num_following': int.parse(following.text),
      'has_profile_picture': hasPhoto,
      'is_private': private,
      'has_external_url': externalLink,
    };
  }

  Widget _count(String title, TextEditingController controller) => Expanded(
    child: TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: title,
        border: const OutlineInputBorder(),
        isDense: true,
      ),
      keyboardType: TextInputType.number,
      inputFormatters: [FilteringTextInputFormatter.digitsOnly],
      validator: (value) {
        final parsed = int.tryParse(value ?? '');
        return parsed == null || parsed < 0 || parsed > 2147483647
            ? 'Invalid count'
            : null;
      },
    ),
  );

  @override
  Widget build(BuildContext context) => Form(
    key: formKey,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Review these demo values. They are not extracted from screenshots or verified by Instagram.',
          style: TextStyle(color: igGrey, fontSize: 12),
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: displayName,
          maxLength: 100,
          decoration: const InputDecoration(
            labelText: 'Display name',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: bio,
          maxLength: 500,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'Profile bio',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _count('Posts', posts),
            const SizedBox(width: 8),
            _count('Followers', followers),
            const SizedBox(width: 8),
            _count('Following', following),
          ],
        ),
        CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          title: const Text('Has a profile photo'),
          value: hasPhoto,
          onChanged: (v) => setState(() => hasPhoto = v!),
        ),
        CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          title: const Text('Private account'),
          value: private,
          onChanged: (v) => setState(() => private = v!),
        ),
        CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          title: const Text('Has an external link'),
          value: externalLink,
          onChanged: (v) => setState(() => externalLink = v!),
        ),
      ],
    ),
  );
}
