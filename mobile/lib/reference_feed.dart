part of 'main.dart';

const referenceAccount = Account(
  'aktobe_typical',
  'Aktobe Typical',
  'Новости и события',
  128,
  5400,
  310,
);

class _HomeShellState extends State<HomeShell> {
  int tab = 0;
  bool unread = true;

  @override
  void initState() {
    super.initState();
    refreshStatuses();
  }

  void notice(String text) =>
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));

  @override
  Widget build(BuildContext context) => ColoredBox(
    color: const Color(0xFFF3F3F3),
    child: Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 430),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final scale = constraints.maxWidth / 390;
            return Scaffold(
              extendBody: true,
              body: SafeArea(
                bottom: false,
                child: Column(
                  children: [
                    if (kIsWeb) ReferenceStatusBar(scale: scale),
                    if (tab == 0)
                      SizedBox(
                        width: double.infinity,
                        height: 50 * scale,
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            Semantics(
                              header: true,
                              label: 'Instagram',
                              child: Image.asset(
                                'assets/reference/wordmark.png',
                                key: const Key('reference-wordmark'),
                                width: 120 * scale,
                                height: 29 * scale,
                                fit: BoxFit.contain,
                              ),
                            ),
                            Positioned(
                              left: 13 * scale,
                              child: IconButton(
                                tooltip: 'Create',
                                icon: Icon(
                                  CupertinoIcons.plus,
                                  size: 28 * scale,
                                ),
                                onPressed: () => notice(
                                  'Создание публикаций пока недоступно в демоверсии.',
                                ),
                              ),
                            ),
                            Positioned(
                              right: 13 * scale,
                              child: IconButton(
                                tooltip: 'Notifications',
                                icon: Icon(
                                  CupertinoIcons.heart,
                                  size: 28 * scale,
                                ),
                                onPressed: () =>
                                    notice('Новых уведомлений нет.'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    Expanded(
                      child: ValueListenableBuilder(
                        valueListenable: statuses,
                        builder: (_, value, child) => switch (tab) {
                          0 => const FeedPage(),
                          1 => const SearchPage(),
                          2 => ProfilePage(
                            account: accounts.first,
                            showHandleBar: true,
                          ),
                          _ => const Center(
                            child: Text('Новых сообщений нет.'),
                          ),
                        },
                      ),
                    ),
                  ],
                ),
              ),
              bottomNavigationBar: Padding(
                padding: EdgeInsets.fromLTRB(
                  20 * scale,
                  0,
                  20 * scale,
                  21 * scale,
                ),
                child: Container(
                  key: const Key('floating-navigation'),
                  height: 58 * scale,
                  padding: EdgeInsets.symmetric(
                    horizontal: 5 * scale,
                    vertical: 4 * scale,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.98),
                    borderRadius: BorderRadius.circular(36 * scale),
                    border: Border.all(
                      color: const Color(0xFFDADADA),
                      width: 0.6,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.06),
                        blurRadius: 7,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      _nav(
                        'Home',
                        CupertinoIcons.house_fill,
                        tab == 0,
                        scale,
                        () => setState(() => tab = 0),
                      ),
                      _nav(
                        'Reels',
                        null,
                        false,
                        scale,
                        () => notice(
                          'Видео Reels пока не добавлены в демоверсию.',
                        ),
                      ),
                      Expanded(
                        child: _navButton(
                          'Messages',
                          false,
                          scale,
                          Stack(
                            clipBehavior: Clip.none,
                            children: [
                              Icon(CupertinoIcons.paperplane, size: 26 * scale),
                              if (unread)
                                Positioned(
                                  right: -7 * scale,
                                  bottom: -7 * scale,
                                  child: Container(
                                    width: 18 * scale,
                                    height: 18 * scale,
                                    alignment: Alignment.center,
                                    decoration: const BoxDecoration(
                                      color: Color(0xFFFF003D),
                                      shape: BoxShape.circle,
                                    ),
                                    child: Text(
                                      '1',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 12 * scale,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                ),
                            ],
                          ),
                          () => setState(() {
                            tab = 3;
                            unread = false;
                          }),
                        ),
                      ),
                      _nav(
                        'Search',
                        CupertinoIcons.search,
                        tab == 1,
                        scale,
                        () => setState(() => tab = 1),
                      ),
                      Expanded(
                        child: _navButton(
                          'Profile',
                          tab == 2,
                          scale,
                          ClipOval(
                            child: Image.asset(
                              'assets/reference/night-story.png',
                              width: 25 * scale,
                              height: 25 * scale,
                              fit: BoxFit.cover,
                            ),
                          ),
                          () => setState(() => tab = 2),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    ),
  );

  Widget _nav(
    String label,
    IconData? icon,
    bool selected,
    double scale,
    VoidCallback onTap,
  ) => Expanded(
    child: _navButton(
      label,
      selected,
      scale,
      icon == null
          ? ReferenceGlyph(kind: 'reels', size: 26 * scale)
          : Icon(icon, size: 26 * scale),
      onTap,
    ),
  );

  Widget _navButton(
    String label,
    bool selected,
    double scale,
    Widget icon,
    VoidCallback onTap,
  ) => Tooltip(
    message: label,
    child: Semantics(
      button: true,
      label: label,
      selected: selected,
      child: Material(
        color: selected ? const Color(0xFFF0F0F0) : Colors.transparent,
        borderRadius: BorderRadius.circular(28 * scale),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(28 * scale),
          child: Center(child: ExcludeSemantics(child: icon)),
        ),
      ),
    ),
  );
}

/// Only rendered in the browser preview; native devices use their own status bar.
class ReferenceStatusBar extends StatelessWidget {
  final double scale;
  const ReferenceStatusBar({super.key, required this.scale});

  @override
  Widget build(BuildContext context) => Semantics(
    label: 'iPhone preview: 12:34, Wi-Fi, battery 48 percent',
    child: ExcludeSemantics(
      child: SizedBox(
        height: 58 * scale,
        child: Padding(
          padding: EdgeInsets.fromLTRB(40 * scale, 0, 35 * scale, 0),
          child: Row(
            children: [
              Text(
                '12:34',
                style: TextStyle(
                  fontSize: 17 * scale,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(width: 3),
              Icon(CupertinoIcons.location_fill, size: 14 * scale),
              const Spacer(),
              ReferenceGlyph(kind: 'signal', size: 20 * scale),
              SizedBox(width: 7 * scale),
              Icon(CupertinoIcons.wifi, size: 21 * scale),
              SizedBox(width: 8 * scale),
              Stack(
                alignment: Alignment.centerLeft,
                children: [
                  Container(
                    width: 25 * scale,
                    height: 14 * scale,
                    decoration: BoxDecoration(
                      color: const Color(0xFFBCBCBC),
                      borderRadius: BorderRadius.circular(4 * scale),
                    ),
                  ),
                  Container(
                    width: 18 * scale,
                    height: 14 * scale,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: const Color(0xFF171717),
                      borderRadius: BorderRadius.circular(4 * scale),
                    ),
                    child: Text(
                      '48',
                      style: TextStyle(
                        fontSize: 11 * scale,
                        height: 1,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

class StoriesRow extends StatelessWidget {
  const StoriesRow({super.key});

  @override
  Widget build(BuildContext context) {
    final scale = MediaQuery.sizeOf(context).width.clamp(0, 430) / 390;
    const names = [
      'Ваша исто...',
      'teemirgali',
      'abilzhan_17',
      'rasultomi',
      'aigerim.k',
    ];
    const assets = [
      'own-story',
      'default-story',
      'sports-story',
      'night-story',
      'own-story',
    ];
    return SizedBox(
      height: 128 * scale,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.fromLTRB(7 * scale, 4 * scale, 8 * scale, 0),
        itemCount: names.length,
        separatorBuilder: (_, index) => SizedBox(width: 12 * scale),
        itemBuilder: (context, index) => SizedBox(
          width: 90 * scale,
          child: Column(
            children: [
              SizedBox(
                height: 91 * scale,
                child: Center(
                  child: Stack(
                    children: [
                      Container(
                        padding: EdgeInsets.all(index == 0 ? 0 : 3 * scale),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: index == 0 ? null : igStoryGradient,
                        ),
                        child: Container(
                          padding: EdgeInsets.all(index == 0 ? 0 : 3 * scale),
                          decoration: const BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.white,
                          ),
                          child: ClipOval(
                            child: Image.asset(
                              'assets/reference/${assets[index]}.png',
                              width: (index == 0 ? 78 : 78) * scale,
                              height: 78 * scale,
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                      ),
                      if (index == 0)
                        Positioned(
                          right: -1 * scale,
                          bottom: -1 * scale,
                          child: Container(
                            width: 29 * scale,
                            height: 29 * scale,
                            decoration: BoxDecoration(
                              color: const Color(0xFF222629),
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: Colors.white,
                                width: 3 * scale,
                              ),
                            ),
                            child: Icon(
                              CupertinoIcons.plus,
                              color: Colors.white,
                              size: 21 * scale,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 3 * scale),
              Text(
                names[index],
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontSize: 15 * scale, letterSpacing: -0.35),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class FeedPage extends StatelessWidget {
  const FeedPage({super.key});

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: refreshStatuses,
    child: ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.only(bottom: 108),
      itemCount: 5,
      itemBuilder: (_, index) {
        if (index == 0) return const StoriesRow();
        return PostCard(
          account: index == 1
              ? referenceAccount
              : accounts[(index - 2) % accounts.length],
          index: index - 1,
        );
      },
    ),
  );
}

class PostCard extends StatefulWidget {
  final Account account;
  final int index;
  const PostCard({super.key, required this.account, required this.index});

  @override
  State<PostCard> createState() => _PostCardState();
}

class _PostCardState extends State<PostCard> {
  bool liked = false;
  bool saved = false;

  @override
  Widget build(BuildContext context) => ValueListenableBuilder(
    valueListenable: statuses,
    builder: (_, value, child) => _buildPost(context),
  );

  Widget _buildPost(BuildContext context) {
    final account = widget.account;
    final isReference = widget.index == 0;
    final scale = MediaQuery.sizeOf(context).width.clamp(0, 430) / 390;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          height: (account.flag == null ? 51 : 72) * scale,
          child: Row(
            children: [
              SizedBox(width: 7 * scale),
              GestureDetector(
                onTap: () => openProfile(context, account),
                child: isReference
                    ? SizedBox(
                        width: 34 * scale,
                        height: 33 * scale,
                        child: Stack(
                          children: [
                            Positioned(
                              right: 0,
                              top: 0,
                              child: ClipOval(
                                child: Image.asset(
                                  'assets/reference/collaborator-avatar.png',
                                  width: 25 * scale,
                                  height: 25 * scale,
                                ),
                              ),
                            ),
                            Positioned(
                              left: 0,
                              bottom: 0,
                              child: Container(
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: Colors.white,
                                    width: 1.3,
                                  ),
                                ),
                                child: ClipOval(
                                  child: Image.asset(
                                    'assets/reference/news-avatar.png',
                                    width: 24 * scale,
                                    height: 24 * scale,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      )
                    : StoryAvatar(account.name, size: 29 * scale),
              ),
              SizedBox(width: 11 * scale),
              Expanded(
                child: GestureDetector(
                  onTap: () => openProfile(context, account),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Flexible(
                            child: Text(
                              account.handle,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontSize: 18 * scale,
                                fontWeight: FontWeight.w600,
                                letterSpacing: -0.55,
                              ),
                            ),
                          ),
                          if (isReference) ...[
                            SizedBox(width: 4 * scale),
                            Icon(
                              Icons.verified,
                              size: 13 * scale,
                              color: const Color(0xFF009AF0),
                            ),
                            Text(
                              ' и Ещё 3',
                              style: TextStyle(
                                fontSize: 18 * scale,
                                fontWeight: FontWeight.w500,
                                letterSpacing: -0.5,
                              ),
                            ),
                          ],
                        ],
                      ),
                      if (account.flag != null) FlagBadge(account.flag!),
                    ],
                  ),
                ),
              ),
              IconButton(
                tooltip: 'More actions',
                icon: ReferenceGlyph(kind: 'filter', size: 26 * scale),
                onPressed: () => showAccountActions(
                  context,
                  account,
                  saved: saved,
                  onSave: () => setState(() => saved = !saved),
                ),
              ),
              SizedBox(width: 3 * scale),
            ],
          ),
        ),
        GestureDetector(
          onDoubleTap: () => setState(() => liked = true),
          child: AspectRatio(
            aspectRatio: 588 / 735,
            child: isReference
                ? Image.asset('assets/reference/post.png', fit: BoxFit.cover)
                : Photo(
                    'post-${account.handle}-${widget.index}',
                    900,
                    widget.index,
                  ),
          ),
        ),
        Row(
          children: [
            IconButton(
              tooltip: liked ? 'Unlike' : 'Like',
              onPressed: () => setState(() => liked = !liked),
              icon: Icon(
                liked ? CupertinoIcons.heart_fill : CupertinoIcons.heart,
                color: liked ? igRed : Colors.black,
                size: 28 * scale,
              ),
            ),
            IconButton(
              tooltip: 'Comments',
              onPressed: () => _comments(context),
              icon: Icon(CupertinoIcons.chat_bubble, size: 26 * scale),
            ),
            IconButton(
              tooltip: 'Share post',
              onPressed: () => _share(context),
              icon: Icon(CupertinoIcons.paperplane, size: 26 * scale),
            ),
            const Spacer(),
            IconButton(
              tooltip: saved ? 'Unsave post' : 'Save post',
              onPressed: () => setState(() => saved = !saved),
              icon: Icon(
                saved ? CupertinoIcons.bookmark_fill : CupertinoIcons.bookmark,
                size: 27 * scale,
              ),
            ),
          ],
        ),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 12 * scale),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '${isReference ? 502 + (liked ? 1 : 0) : 120 + (liked ? 1 : 0)} отметок «Нравится»',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14 * scale,
                ),
              ),
              SizedBox(height: 5 * scale),
              Text.rich(
                TextSpan(
                  children: [
                    TextSpan(
                      text: '${account.handle} ',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    TextSpan(
                      text: isReference
                          ? 'Новости региона. Фото из присланного референса.'
                          : captions[widget.index % captions.length],
                    ),
                  ],
                ),
                style: TextStyle(fontSize: 14 * scale),
              ),
              SizedBox(height: 4 * scale),
              Text(
                '2 часа назад',
                style: TextStyle(color: igGrey, fontSize: 11 * scale),
              ),
              SizedBox(height: 18 * scale),
            ],
          ),
        ),
      ],
    );
  }

  void _comments(BuildContext context) => showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    backgroundColor: Colors.white,
    builder: (_) => const SafeArea(
      child: SizedBox(
        height: 180,
        child: Center(child: Text('Комментариев пока нет.')),
      ),
    ),
  );

  void _share(BuildContext context) => showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    backgroundColor: Colors.white,
    builder: (_) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Text(
          '@${widget.account.handle} — публикация в локальной демоверсии',
        ),
      ),
    ),
  );
}

class ReferenceGlyph extends StatelessWidget {
  final String kind;
  final double size;
  const ReferenceGlyph({super.key, required this.kind, required this.size});

  @override
  Widget build(BuildContext context) => SizedBox.square(
    dimension: size,
    child: CustomPaint(painter: _ReferenceGlyphPainter(kind)),
  );
}

class _ReferenceGlyphPainter extends CustomPainter {
  final String kind;
  const _ReferenceGlyphPainter(this.kind);

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / 28, size.height / 28);
    final paint = Paint()
      ..color = const Color(0xFF111517)
      ..strokeWidth = 2.1
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    if (kind == 'filter') {
      canvas.drawLine(const Offset(5, 9), const Offset(23, 9), paint);
      canvas.drawLine(const Offset(5, 17), const Offset(17, 17), paint);
    } else if (kind == 'reels') {
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          const Rect.fromLTWH(5, 3, 19, 23),
          const Radius.circular(5.5),
        ),
        paint,
      );
      canvas.drawPath(
        Path()
          ..moveTo(11, 8)
          ..lineTo(19, 14)
          ..lineTo(11, 20)
          ..close(),
        paint,
      );
    } else {
      paint.style = PaintingStyle.fill;
      for (var i = 0; i < 4; i++) {
        paint.color = i < 2 ? const Color(0xFF111517) : const Color(0xFFC7C7C7);
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(2 + i * 6, 12 - i * 2.5, 4, 10 + i * 2.5),
            const Radius.circular(1.7),
          ),
          paint,
        );
        canvas.drawCircle(Offset(4 + i * 6, 26), 1.8, paint);
      }
    }
  }

  @override
  bool shouldRepaint(_ReferenceGlyphPainter oldDelegate) =>
      oldDelegate.kind != kind;
}
