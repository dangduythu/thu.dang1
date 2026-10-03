import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Alert,
  BackHandler,
  KeyboardAvoidingView,
  PanResponder,
  Platform,
  Pressable,
  ScrollView,
  Share,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaProvider, SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';

const BOOK = require('./src/data/book.json');
const STORAGE_KEY = 'tu_duy_dung_mobile_v1_state';

const COLORS = {
  light: {
    bg: '#eef4fb',
    card: '#ffffff',
    text: '#14213d',
    muted: '#64748b',
    line: '#d8e3f0',
    navy: '#274472',
    primary: '#2563eb',
    primarySoft: '#dbeafe',
    green: '#15803d',
    greenSoft: '#dcfce7',
    purple: '#7c3aed',
    purpleSoft: '#ede9fe',
    orange: '#c2410c',
    orangeSoft: '#fff7ed',
    red: '#b91c1c',
    redSoft: '#fee2e2',
    cyan: '#0e7490',
    cyanSoft: '#ecfeff',
    input: '#ffffff',
  },
  dark: {
    bg: '#0f172a',
    card: '#172033',
    text: '#eef2ff',
    muted: '#a8b3c7',
    line: '#334155',
    navy: '#bfdbfe',
    primary: '#60a5fa',
    primarySoft: '#1e3a5f',
    green: '#4ade80',
    greenSoft: '#173b2a',
    purple: '#c4b5fd',
    purpleSoft: '#312e55',
    orange: '#fdba74',
    orangeSoft: '#442719',
    red: '#fca5a5',
    redSoft: '#471f24',
    cyan: '#67e8f9',
    cyanSoft: '#164e63',
    input: '#111827',
  },
};

const DEFAULT_STATE = {
  language: 'BI',
  theme: 'light',
  fontScale: 1,
  readLessons: [],
  bookmarks: [],
  quizScores: {},
  caseResults: {},
  notes: {},
  workbenchDocs: {},
  reviewState: {},
  lessonScroll: {},
  lastLesson: '1.1',
};

const ALL_LESSONS = BOOK.chapters.flatMap((c) => c.lessons);
const LESSON_BY_ID = Object.fromEntries(ALL_LESSONS.map((x) => [x.id, x]));
const CHAPTER_BY_LESSON = {};
BOOK.chapters.forEach((c, i) => c.lessons.forEach((l) => { CHAPTER_BY_LESSON[l.id] = i; }));

const fmt = (lang, vi, en) => {
  if (lang === 'VI') return vi;
  if (lang === 'EN') return en;
  return `${vi} / ${en}`;
};

const todayISO = () => new Date().toISOString().slice(0, 10);
const addDaysISO = (days) => {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
};

function PressButton({ title, onPress, colors, kind = 'primary', style, disabled = false }) {
  const bg = kind === 'primary' ? colors.primary : kind === 'danger' ? colors.redSoft : colors.card;
  const fg = kind === 'primary' ? '#ffffff' : kind === 'danger' ? colors.red : colors.text;
  return (
    <Pressable
      disabled={disabled}
      onPress={onPress}
      android_ripple={{ color: '#ffffff33' }}
      style={({ pressed }) => [
        styles.button,
        { backgroundColor: bg, borderColor: kind === 'primary' ? bg : colors.line, opacity: disabled ? 0.45 : pressed ? 0.82 : 1 },
        style,
      ]}
    >
      <Text style={[styles.buttonText, { color: fg }]}>{title}</Text>
    </Pressable>
  );
}

function LanguagePills({ lang, setLang, colors }) {
  return (
    <View style={[styles.segment, { backgroundColor: colors.primarySoft, borderColor: colors.line }]}>
      {['BI', 'VI', 'EN'].map((x) => (
        <Pressable
          key={x}
          onPress={() => setLang(x)}
          style={[styles.segmentItem, lang === x && { backgroundColor: colors.card }]}
        >
          <Text style={{ color: lang === x ? colors.primary : colors.muted, fontWeight: '800' }}>{x}</Text>
        </Pressable>
      ))}
    </View>
  );
}

function AppHeader({ title, subtitle, canBack, onBack, right, colors, focus = false }) {
  if (focus) return null;
  return (
    <View style={[styles.header, { backgroundColor: colors.card, borderBottomColor: colors.line }]}>
      <View style={styles.headerRow}>
        {canBack ? (
          <Pressable onPress={onBack} style={styles.iconButton} hitSlop={8}>
            <Text style={[styles.backGlyph, { color: colors.text }]}>‹</Text>
          </Pressable>
        ) : <View style={styles.iconButton} />}
        <View style={styles.headerCenter}>
          <Text numberOfLines={1} style={[styles.headerTitle, { color: colors.text }]}>{title}</Text>
          {!!subtitle && <Text numberOfLines={1} style={[styles.headerSubtitle, { color: colors.muted }]}>{subtitle}</Text>}
        </View>
        <View style={styles.headerRight}>{right}</View>
      </View>
    </View>
  );
}

function BilingualBlock({ vi, en, lang, colors, fontScale = 1, compact = false }) {
  const bodyStyle = [styles.bodyText, { color: colors.text, fontSize: 16 * fontScale, lineHeight: 24 * fontScale }];
  if (lang === 'VI') return <Text selectable style={bodyStyle}>{vi}</Text>;
  if (lang === 'EN') return <Text selectable style={bodyStyle}>{en}</Text>;
  return (
    <View>
      <Text style={[styles.langBadge, { color: colors.primary }]}>VI • TIẾNG VIỆT</Text>
      <Text selectable style={bodyStyle}>{vi}</Text>
      <View style={[styles.divider, { backgroundColor: colors.line, marginVertical: compact ? 8 : 12 }]} />
      <Text style={[styles.langBadge, { color: colors.purple }]}>EN • ENGLISH</Text>
      <Text selectable style={bodyStyle}>{en}</Text>
    </View>
  );
}

function SectionCard({ title, titleEn, vi, en, lang, colors, fontScale, tone = 'blue', children }) {
  const tones = {
    blue: [colors.primarySoft, colors.primary],
    green: [colors.greenSoft, colors.green],
    orange: [colors.orangeSoft, colors.orange],
    red: [colors.redSoft, colors.red],
    purple: [colors.purpleSoft, colors.purple],
    cyan: [colors.cyanSoft, colors.cyan],
  };
  const [soft, fg] = tones[tone] || tones.blue;
  return (
    <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
      <View style={[styles.cardTitleBar, { backgroundColor: soft }]}>
        <Text style={[styles.cardTitle, { color: fg }]}>{fmt(lang, title, titleEn)}</Text>
      </View>
      <View style={styles.cardBody}>
        {children || <BilingualBlock vi={vi} en={en} lang={lang} colors={colors} fontScale={fontScale} />}
      </View>
    </View>
  );
}

function BulletList({ vi = [], en = [], lang, colors, fontScale }) {
  const list = lang === 'VI' ? [{ tag: '', items: vi }] : lang === 'EN' ? [{ tag: '', items: en }] : [
    { tag: 'VI • TIẾNG VIỆT', items: vi, tint: colors.primary },
    { tag: 'EN • ENGLISH', items: en, tint: colors.purple },
  ];
  return (
    <View>
      {list.map((group, gi) => (
        <View key={gi} style={gi > 0 ? { marginTop: 12 } : undefined}>
          {!!group.tag && <Text style={[styles.langBadge, { color: group.tint }]}>{group.tag}</Text>}
          {group.items.map((item, i) => (
            <View key={i} style={styles.bulletRow}>
              <Text style={[styles.bulletDot, { color: colors.primary }]}>•</Text>
              <Text selectable style={[styles.bodyText, { color: colors.text, fontSize: 16 * fontScale, lineHeight: 24 * fontScale, flex: 1 }]}>{item}</Text>
            </View>
          ))}
        </View>
      ))}
    </View>
  );
}

function BottomNav({ screen, goRoot, colors, hidden }) {
  const insets = useSafeAreaInsets();
  if (hidden) return null;
  const items = [
    ['home', '⌂', 'Home'],
    ['library', '▤', 'Book'],
    ['review', '◆', 'Review'],
    ['workbench', '▣', 'Apply'],
    ['more', '•••', 'More'],
  ];
  return (
    <View style={[styles.bottomNav, { backgroundColor: colors.card, borderTopColor: colors.line, paddingBottom: Math.max(insets.bottom, 6) }]}>
      {items.map(([name, icon, label]) => {
        const active = screen.name === name || (name === 'library' && screen.name === 'lesson') || (name === 'workbench' && screen.name === 'workbenchForm');
        return (
          <Pressable key={name} onPress={() => goRoot(name)} style={styles.navItem}>
            <Text style={[styles.navIcon, { color: active ? colors.primary : colors.muted }]}>{icon}</Text>
            <Text style={[styles.navLabel, { color: active ? colors.primary : colors.muted }]}>{label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

function ScrollScreen({ children, contentRef, onScroll, colors, keyboard = false }) {
  const content = (
    <ScrollView
      ref={contentRef}
      keyboardShouldPersistTaps="handled"
      keyboardDismissMode="on-drag"
      showsVerticalScrollIndicator={false}
      scrollEventThrottle={300}
      onScroll={onScroll}
      contentContainerStyle={styles.scrollContent}
      style={{ flex: 1, backgroundColor: colors.bg }}
    >
      {children}
    </ScrollView>
  );
  if (!keyboard) return content;
  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      {content}
    </KeyboardAvoidingView>
  );
}

function HomeScreen({ ctx }) {
  const { state, colors, lang, go, progress } = ctx;
  return (
    <ScrollScreen colors={colors}>
      <View style={[styles.hero, { backgroundColor: colors.card, borderColor: colors.line }]}>
        <Text style={[styles.heroKicker, { color: colors.primary }]}>TƯ DUY ĐÚNG • THINK RIGHT</Text>
        <Text style={[styles.heroTitle, { color: colors.text }]}>Mobile V1.0</Text>
        <Text style={[styles.heroText, { color: colors.muted }]}>
          {fmt(lang, 'Đọc • Hiểu • Nhớ • Áp dụng', 'Read • Understand • Remember • Apply')}
        </Text>
        <View style={styles.heroActions}>
          <PressButton title={fmt(lang, '▶ Tiếp tục đọc', '▶ Continue')} onPress={() => go('lesson', { id: state.lastLesson || '1.1' })} colors={colors} style={{ flex: 1 }} />
          <PressButton title={fmt(lang, 'Ôn hôm nay', 'Review due')} onPress={() => go('review')} colors={colors} kind="secondary" style={{ flex: 1 }} />
        </View>
      </View>

      <View style={styles.statsGrid}>
        {[
          [`${progress.read}/40`, fmt(lang, 'Đã đọc', 'Read')],
          [`${progress.quiz}/40`, 'Quiz'],
          [String(progress.due), fmt(lang, 'Cần ôn', 'Due')],
          [String(progress.notes), fmt(lang, 'Ghi chú', 'Notes')],
        ].map(([value, label], i) => (
          <View key={i} style={[styles.statCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <Text style={[styles.statValue, { color: colors.text }]}>{value}</Text>
            <Text style={[styles.statLabel, { color: colors.muted }]}>{label}</Text>
          </View>
        ))}
      </View>

      <Text style={[styles.sectionHeading, { color: colors.text }]}>{fmt(lang, 'Học và áp dụng', 'Learn and apply')}</Text>
      {[
        ['library', '📘', '40 bài học', '40 lessons', 'Đọc song ngữ, câu chuyện, sơ đồ, ví dụ.', 'Bilingual reading, stories, memory maps, examples.'],
        ['quizHome', '✅', 'Quiz 4 câu/bài', '4-question quizzes', 'Kiểm tra nhanh sau từng bài.', 'Quick checks after every lesson.'],
        ['caseLab', '🧭', 'Case Lab', 'Case Lab', 'Tình huống nhiều bước, feedback ngay.', 'Multi-step scenarios with instant feedback.'],
        ['workbench', '🧰', 'Workbench', 'Workbench', '5 Why, PDCA, A3, RACI, Risk, Decision, Skill.', '5 Why, PDCA, A3, RACI, Risk, Decision, Skill.'],
      ].map(([route, icon, tvi, ten, svi, sen]) => (
        <Pressable key={route} onPress={() => go(route)} style={({ pressed }) => [styles.featureCard, { backgroundColor: colors.card, borderColor: colors.line, opacity: pressed ? 0.8 : 1 }]}>
          <Text style={styles.featureIcon}>{icon}</Text>
          <View style={{ flex: 1 }}>
            <Text style={[styles.featureTitle, { color: colors.text }]}>{fmt(lang, tvi, ten)}</Text>
            <Text style={[styles.featureSub, { color: colors.muted }]}>{fmt(lang, svi, sen)}</Text>
          </View>
          <Text style={[styles.chevron, { color: colors.muted }]}>›</Text>
        </Pressable>
      ))}
    </ScrollScreen>
  );
}

function LibraryScreen({ ctx }) {
  const { colors, lang, go, state } = ctx;
  const [query, setQuery] = useState('');
  const q = query.trim().toLowerCase();
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Mục lục', 'Contents')}</Text>
      <TextInput
        value={query}
        onChangeText={setQuery}
        placeholder={fmt(lang, 'Tìm bài, từ khóa...', 'Search lessons, keywords...')}
        placeholderTextColor={colors.muted}
        style={[styles.searchInput, { backgroundColor: colors.input, color: colors.text, borderColor: colors.line }]}
        returnKeyType="search"
      />
      {BOOK.chapters.map((chapter, ci) => {
        const enCh = BOOK.enChapters[String(ci + 1)] || {};
        const lessons = chapter.lessons.filter((l) => {
          if (!q) return true;
          const e = BOOK.enLessons[l.id] || {};
          return [l.id, l.title, l.summary, l.concept, e.title, e.summary, e.concept].join(' ').toLowerCase().includes(q);
        });
        if (!lessons.length) return null;
        return (
          <View key={ci} style={[styles.chapterCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <Text style={[styles.chapterNumber, { color: colors.primary }]}>{String(ci + 1).padStart(2, '0')}</Text>
            <View style={{ flex: 1 }}>
              <Text style={[styles.chapterTitle, { color: colors.text }]}>{fmt(lang, chapter.title, enCh.title || chapter.title)}</Text>
              <Text style={[styles.chapterSub, { color: colors.muted }]}>{fmt(lang, chapter.subtitle, enCh.subtitle || chapter.subtitle)}</Text>
              <View style={{ marginTop: 10 }}>
                {lessons.map((l) => {
                  const e = BOOK.enLessons[l.id];
                  const read = state.readLessons.includes(l.id);
                  const saved = state.bookmarks.includes(l.id);
                  return (
                    <Pressable key={l.id} onPress={() => go('lesson', { id: l.id })} style={({ pressed }) => [styles.lessonRow, { borderTopColor: colors.line, opacity: pressed ? 0.72 : 1 }]}>
                      <Text style={[styles.lessonId, { color: colors.primary }]}>{read ? '✓ ' : ''}{l.id}</Text>
                      <Text style={[styles.lessonRowText, { color: colors.text }]} numberOfLines={3}>{fmt(lang, l.title, e.title)}</Text>
                      {!!saved && <Text style={{ color: '#f59e0b', fontSize: 18 }}>★</Text>}
                      <Text style={[styles.chevron, { color: colors.muted }]}>›</Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>
          </View>
        );
      })}
    </ScrollScreen>
  );
}

function LessonScreen({ ctx, id }) {
  const { colors, lang, state, setState, go, back, fontScale, focus, setFocus } = ctx;
  const lesson = LESSON_BY_ID[id] || LESSON_BY_ID['1.1'];
  const en = BOOK.enLessons[id] || {};
  const story = BOOK.stories[id] || {};
  const enStory = BOOK.enStories[id] || {};
  const scrollRef = useRef(null);
  const idx = ALL_LESSONS.findIndex((x) => x.id === id);
  const isBookmarked = state.bookmarks.includes(id);
  const isRead = state.readLessons.includes(id);

  useEffect(() => {
    setState((s) => ({ ...s, lastLesson: id }));
    const y = Number(state.lessonScroll[id] || 0);
    if (y > 0) setTimeout(() => scrollRef.current?.scrollTo({ y, animated: false }), 80);
  }, [id]);

  const toggleBookmark = () => setState((s) => ({
    ...s,
    bookmarks: s.bookmarks.includes(id) ? s.bookmarks.filter((x) => x !== id) : [...s.bookmarks, id],
  }));
  const markRead = () => setState((s) => ({
    ...s,
    readLessons: s.readLessons.includes(id) ? s.readLessons : [...s.readLessons, id],
  }));

  const checklistEn = (en.blocks || []).slice(0, 3).map((b) => `Have we clearly defined ${String(b[0]).toLowerCase()}?`).concat(['Do we have data or a practical example to verify it?']);

  return (
    <View style={{ flex: 1 }}>
      <AppHeader
        title={fmt(lang, lesson.title, en.title || lesson.title)}
        subtitle={`${fmt(lang, 'Bài', 'Lesson')} ${idx + 1}/40`}
        canBack
        onBack={back}
        focus={focus}
        colors={colors}
        right={<Pressable onPress={() => setFocus(!focus)} style={styles.iconButton}><Text style={{ color: colors.primary, fontWeight: '900' }}>{focus ? '▣' : '⛶'}</Text></Pressable>}
      />
      {focus && (
        <View style={[styles.focusBar, { backgroundColor: colors.card, borderBottomColor: colors.line }]}>
          <Pressable onPress={() => setFocus(false)} style={styles.focusExit}><Text style={{ color: colors.primary, fontWeight: '800' }}>‹ {fmt(lang, 'Thoát tập trung', 'Exit focus')}</Text></Pressable>
          <Text style={{ color: colors.muted, fontWeight: '700' }}>{idx + 1}/40</Text>
        </View>
      )}
      <ScrollScreen
        contentRef={scrollRef}
        colors={colors}
        onScroll={(e) => {
          const y = e.nativeEvent.contentOffset.y;
          setState((s) => ({ ...s, lessonScroll: { ...s.lessonScroll, [id]: y } }));
        }}
      >
        <View style={[styles.lessonHero, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <Text style={[styles.heroKicker, { color: colors.primary }]}>{fmt(lang, 'BÀI', 'LESSON')} {id}</Text>
          <Text style={[styles.lessonTitle, { color: colors.text, fontSize: 28 * fontScale }]}>{fmt(lang, lesson.title, en.title || '')}</Text>
          <Text style={[styles.lessonSummary, { color: colors.muted, fontSize: 16 * fontScale }]}>{fmt(lang, lesson.summary, en.summary || '')}</Text>
          <View style={styles.lessonActions}>
            <PressButton title={isBookmarked ? '★ Saved' : '☆ Save'} onPress={toggleBookmark} colors={colors} kind="secondary" style={{ flex: 1 }} />
            <PressButton title={isRead ? '✓ Read' : '✓ Mark read'} onPress={markRead} colors={colors} kind="secondary" style={{ flex: 1 }} />
            <PressButton title="Quiz" onPress={() => go('quiz', { id })} colors={colors} style={{ flex: 1 }} />
          </View>
          <PressButton title={fmt(lang, '📝 Ghi chú bài này', '📝 Lesson notes')} onPress={() => go('notes', { id })} colors={colors} kind="secondary" />
        </View>

        <SectionCard title="Sơ đồ ghi nhớ" titleEn="Memory map" lang={lang} colors={colors} fontScale={fontScale} tone="blue">
          <View>
            {(lesson.blocks || []).map((b, i) => {
              const eb = (en.blocks || [])[i] || ['', ''];
              return (
                <View key={i} style={[styles.memoryStep, { backgroundColor: i % 2 ? colors.greenSoft : colors.primarySoft, borderColor: colors.line }]}>
                  <Text style={[styles.memoryIndex, { color: colors.primary }]}>{String(i + 1).padStart(2, '0')}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.memoryTitle, { color: colors.text }]}>{fmt(lang, String(b[0]), String(eb[0]))}</Text>
                    <BilingualBlock vi={String(b[1])} en={String(eb[1])} lang={lang} colors={colors} fontScale={fontScale} compact />
                  </View>
                </View>
              );
            })}
          </View>
        </SectionCard>

        <SectionCard title="Câu chuyện ghi nhớ" titleEn="Memory story" lang={lang} colors={colors} fontScale={fontScale} tone="orange">
          <Text style={[styles.storyTitle, { color: colors.text }]}>{fmt(lang, story.title || '', enStory.title || '')}</Text>
          <BilingualBlock vi={story.story || ''} en={enStory.story || ''} lang={lang} colors={colors} fontScale={fontScale} />
          <View style={[styles.takeaway, { backgroundColor: colors.primarySoft, borderColor: colors.line }]}>
            <Text style={[styles.langBadge, { color: colors.primary }]}>💡 {fmt(lang, 'Điểm cần nhớ', 'Key takeaway')}</Text>
            <Text style={[styles.bodyText, { color: colors.text, fontWeight: '700', fontSize: 16 * fontScale, lineHeight: 24 * fontScale }]}>{fmt(lang, story.memory || '', enStory.memory || '')}</Text>
          </View>
        </SectionCard>

        <SectionCard title="Khái niệm" titleEn="Concept" vi={lesson.concept} en={en.concept || ''} lang={lang} colors={colors} fontScale={fontScale} />
        <SectionCard title="Cách áp dụng" titleEn="How to apply" vi={lesson.method || lesson.apply || ''} en={en.method || ''} lang={lang} colors={colors} fontScale={fontScale} tone="green" />
        <SectionCard title="Tại sao quan trọng?" titleEn="Why it matters" vi={lesson.why || ''} en={en.why || ''} lang={lang} colors={colors} fontScale={fontScale} tone="orange" />
        <SectionCard title="Sai lầm thường gặp" titleEn="Common mistakes" lang={lang} colors={colors} fontScale={fontScale} tone="red">
          <BulletList vi={lesson.mistakes || []} en={en.mistakes || []} lang={lang} colors={colors} fontScale={fontScale} />
        </SectionCard>
        <SectionCard title="Ví dụ thực tế" titleEn="Practical example" vi={lesson.example || ''} en={en.example || ''} lang={lang} colors={colors} fontScale={fontScale} tone="orange" />
        <SectionCard title="Checklist" titleEn="Checklist" lang={lang} colors={colors} fontScale={fontScale} tone="green">
          <BulletList vi={lesson.checklist || []} en={checklistEn} lang={lang} colors={colors} fontScale={fontScale} />
        </SectionCard>
        <SectionCard title="Bài tập áp dụng ngay" titleEn="Apply now" vi={lesson.practice || ''} en={en.practice || ''} lang={lang} colors={colors} fontScale={fontScale} tone="purple" />
        <SectionCard title="Câu hỏi tự phản tư" titleEn="Reflection questions" lang={lang} colors={colors} fontScale={fontScale} tone="cyan">
          <BulletList vi={lesson.reflect || []} en={en.reflect || []} lang={lang} colors={colors} fontScale={fontScale} />
        </SectionCard>

        <View style={styles.prevNextRow}>
          <PressButton title="‹ Prev" onPress={() => idx > 0 && go('lesson', { id: ALL_LESSONS[idx - 1].id }, true)} colors={colors} kind="secondary" disabled={idx === 0} style={{ flex: 1 }} />
          <PressButton title="Next ›" onPress={() => idx < 39 && go('lesson', { id: ALL_LESSONS[idx + 1].id }, true)} colors={colors} disabled={idx === 39} style={{ flex: 1 }} />
        </View>
      </ScrollScreen>
    </View>
  );
}

function QuizHome({ ctx }) {
  const { colors, lang, go, state } = ctx;
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Quiz theo bài', 'Lesson quizzes')}</Text>
      <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{fmt(lang, 'Mỗi bài 4 câu. Điểm cao nhất được lưu.', 'Four questions per lesson. Best score is saved.')}</Text>
      {ALL_LESSONS.map((l) => (
        <Pressable key={l.id} onPress={() => go('quiz', { id: l.id })} style={[styles.simpleRow, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <Text style={[styles.lessonId, { color: colors.primary }]}>{l.id}</Text>
          <Text numberOfLines={2} style={[styles.lessonRowText, { color: colors.text }]}>{fmt(lang, l.title, BOOK.enLessons[l.id].title)}</Text>
          <Text style={{ color: colors.green, fontWeight: '900' }}>{state.quizScores[l.id] != null ? `${state.quizScores[l.id]}%` : '—'}</Text>
          <Text style={[styles.chevron, { color: colors.muted }]}>›</Text>
        </Pressable>
      ))}
    </ScrollScreen>
  );
}

function QuizScreen({ ctx, id }) {
  const { colors, lang, state, setState, back, go, fontScale } = ctx;
  const viq = BOOK.quizVi[id] || [];
  const enq = BOOK.quizEn[id] || [];
  const lesson = LESSON_BY_ID[id];
  const [index, setIndex] = useState(0);
  const [choice, setChoice] = useState(null);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [done, setDone] = useState(false);

  const submit = () => {
    if (choice == null) return;
    const ok = choice === viq[index].answer;
    setFeedback(ok);
    if (ok) setScore((x) => x + 1);
  };
  const next = () => {
    if (index + 1 >= viq.length) {
      const finalScore = Math.round((score + (feedback && choice === viq[index].answer ? 0 : 0)) * 100 / viq.length);
      // score already incremented asynchronously; calculate from selections by using current feedback.
      const actual = Math.round((score + (feedback ? 0 : 0)) * 100 / viq.length);
      const pct = Math.max(actual, feedback ? Math.round(score * 100 / viq.length) : actual);
      const safePct = Math.round(score * 100 / viq.length);
      setState((s) => ({ ...s, quizScores: { ...s.quizScores, [id]: Math.max(Number(s.quizScores[id] || 0), safePct) } }));
      setDone(true);
      return;
    }
    setIndex((x) => x + 1);
    setChoice(null);
    setFeedback(null);
  };

  // avoid async score ambiguity on final step
  const finish = () => {
    const final = score;
    const pct = Math.round(final * 100 / viq.length);
    setState((s) => ({ ...s, quizScores: { ...s.quizScores, [id]: Math.max(Number(s.quizScores[id] || 0), pct) } }));
    setDone(true);
  };

  if (done) {
    const pct = Math.round(score * 100 / viq.length);
    return (
      <View style={{ flex: 1 }}>
        <AppHeader title="Quiz" canBack onBack={back} colors={colors} />
        <ScrollScreen colors={colors}>
          <View style={[styles.resultCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <Text style={styles.resultEmoji}>{pct >= 80 ? '🏆' : pct >= 50 ? '👍' : '📚'}</Text>
            <Text style={[styles.resultTitle, { color: colors.text }]}>{pct}%</Text>
            <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{score}/{viq.length} {fmt(lang, 'câu đúng', 'correct')}</Text>
            <PressButton title={fmt(lang, 'Làm lại', 'Try again')} onPress={() => { setIndex(0); setChoice(null); setScore(0); setFeedback(null); setDone(false); }} colors={colors} />
            <PressButton title={fmt(lang, 'Quay lại bài học', 'Back to lesson')} onPress={() => go('lesson', { id }, true)} colors={colors} kind="secondary" />
          </View>
        </ScrollScreen>
      </View>
    );
  }

  const qv = viq[index];
  const qe = enq[index];
  return (
    <View style={{ flex: 1 }}>
      <AppHeader title={fmt(lang, lesson.title, BOOK.enLessons[id].title)} subtitle={`Quiz ${index + 1}/${viq.length}`} canBack onBack={back} colors={colors} />
      <ScrollScreen colors={colors}>
        <View style={[styles.quizProgress, { backgroundColor: colors.line }]}>
          <View style={[styles.quizProgressFill, { backgroundColor: colors.primary, width: `${((index + 1) / viq.length) * 100}%` }]} />
        </View>
        <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <View style={styles.cardBody}>
            <Text style={[styles.quizQuestion, { color: colors.text, fontSize: 20 * fontScale }]}>{fmt(lang, qv.question, qe.question)}</Text>
            {qv.options.map((opt, i) => {
              const selected = choice === i;
              const correct = feedback != null && i === qv.answer;
              const wrong = feedback === false && selected;
              const bg = correct ? colors.greenSoft : wrong ? colors.redSoft : selected ? colors.primarySoft : colors.card;
              const border = correct ? colors.green : wrong ? colors.red : selected ? colors.primary : colors.line;
              return (
                <Pressable disabled={feedback != null} key={i} onPress={() => setChoice(i)} style={[styles.option, { backgroundColor: bg, borderColor: border }]}>
                  <Text style={[styles.optionLetter, { color: border }]}>{String.fromCharCode(65 + i)}</Text>
                  <Text style={[styles.optionText, { color: colors.text, fontSize: 15 * fontScale }]}>{fmt(lang, opt, qe.options[i])}</Text>
                </Pressable>
              );
            })}
            {feedback != null && (
              <View style={[styles.feedback, { backgroundColor: feedback ? colors.greenSoft : colors.redSoft }]}>
                <Text style={{ color: feedback ? colors.green : colors.red, fontWeight: '900', marginBottom: 6 }}>{feedback ? fmt(lang, '✓ Chính xác', '✓ Correct') : fmt(lang, '✕ Chưa đúng', '✕ Not correct')}</Text>
                <BilingualBlock vi={qv.explain} en={qe.explain} lang={lang} colors={colors} fontScale={fontScale} compact />
              </View>
            )}
            {feedback == null ? (
              <PressButton title={fmt(lang, 'Kiểm tra', 'Check')} onPress={submit} disabled={choice == null} colors={colors} />
            ) : index + 1 === viq.length ? (
              <PressButton title={fmt(lang, 'Xem kết quả', 'See result')} onPress={finish} colors={colors} />
            ) : (
              <PressButton title={fmt(lang, 'Câu tiếp theo', 'Next question')} onPress={next} colors={colors} />
            )}
          </View>
        </View>
      </ScrollScreen>
    </View>
  );
}

function ReviewScreen({ ctx }) {
  const { colors, lang, state, setState, fontScale } = ctx;
  const dueIds = ALL_LESSONS.map((x) => x.id).filter((id) => {
    const r = state.reviewState[id];
    return !r || (r.due || todayISO()) <= todayISO();
  });
  const ids = dueIds.length ? dueIds : ALL_LESSONS.map((x) => x.id);
  const [pos, setPos] = useState(0);
  const [show, setShow] = useState(false);
  const id = ids[pos % ids.length];
  const card = BOOK.flashcards[id];
  const rs = state.reviewState[id] || { level: 0, due: todayISO(), reviews: 0 };

  const rate = (kind) => {
    const current = Number(rs.level || 0);
    let level = current;
    let due = addDaysISO(3);
    if (kind === 'hard') { level = Math.max(0, current - 1); due = addDaysISO(1); }
    if (kind === 'good') { level = Math.min(6, current + 1); due = addDaysISO([1, 3, 7, 14, 30, 60, 90][level]); }
    if (kind === 'easy') { level = Math.min(6, current + 2); due = addDaysISO([3, 7, 14, 30, 60, 90, 120][Math.min(6, level)]); }
    setState((s) => ({ ...s, reviewState: { ...s.reviewState, [id]: { level, due, reviews: Number(rs.reviews || 0) + 1 } } }));
    setShow(false);
    setPos((p) => (p + 1) % ids.length);
  };

  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Ôn tập thông minh', 'Smart Review')}</Text>
      <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{fmt(lang, `Đến hạn hôm nay: ${dueIds.length}`, `Due today: ${dueIds.length}`)}</Text>
      <View style={[styles.flashCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
        <Text style={[styles.heroKicker, { color: colors.primary }]}>{id} • Level {rs.level || 0}</Text>
        <Text style={[styles.flashFront, { color: colors.text, fontSize: 28 * fontScale }]}>{fmt(lang, card.front_vi, card.front_en)}</Text>
        {!show ? (
          <>
            <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{fmt(lang, 'Tự nhớ lại ý chính trước khi mở đáp án.', 'Recall the key idea before revealing the answer.')}</Text>
            <PressButton title={fmt(lang, 'Hiện đáp án', 'Reveal answer')} onPress={() => setShow(true)} colors={colors} />
          </>
        ) : (
          <>
            <View style={[styles.divider, { backgroundColor: colors.line }]} />
            <BilingualBlock vi={card.back_vi} en={card.back_en} lang={lang} colors={colors} fontScale={fontScale} />
            <View style={styles.rateRow}>
              <PressButton title={fmt(lang, 'Khó', 'Hard')} onPress={() => rate('hard')} colors={colors} kind="danger" style={{ flex: 1 }} />
              <PressButton title={fmt(lang, 'Tốt', 'Good')} onPress={() => rate('good')} colors={colors} kind="secondary" style={{ flex: 1 }} />
              <PressButton title={fmt(lang, 'Dễ', 'Easy')} onPress={() => rate('easy')} colors={colors} style={{ flex: 1 }} />
            </View>
          </>
        )}
      </View>
      <Text style={[styles.smallNote, { color: colors.muted }]}>{fmt(lang, 'Dữ liệu ôn tập được lưu offline trên máy.', 'Review data is stored offline on the device.')}</Text>
    </ScrollScreen>
  );
}

function CaseLabHome({ ctx }) {
  const { colors, lang, go, state } = ctx;
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>Case Lab</Text>
      <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{fmt(lang, 'Tình huống nhiều bước – ra quyết định theo diễn biến.', 'Multi-step scenarios – make decisions as the situation unfolds.')}</Text>
      {BOOK.multiCases.map((c) => (
        <Pressable key={c.id} onPress={() => go('caseRun', { id: c.id })} style={[styles.featureCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <Text style={styles.featureIcon}>🧭</Text>
          <View style={{ flex: 1 }}>
            <Text style={[styles.featureTitle, { color: colors.text }]}>{fmt(lang, c.title_vi, c.title_en)}</Text>
            <Text style={[styles.featureSub, { color: colors.muted }]}>{fmt(lang, c.intro_vi, c.intro_en)}</Text>
            <Text style={{ color: colors.green, fontWeight: '800', marginTop: 6 }}>{state.caseResults[c.id] != null ? `${state.caseResults[c.id]}%` : `${c.steps.length} steps`}</Text>
          </View>
          <Text style={[styles.chevron, { color: colors.muted }]}>›</Text>
        </Pressable>
      ))}
    </ScrollScreen>
  );
}

function CaseRun({ ctx, id }) {
  const { colors, lang, back, setState, fontScale } = ctx;
  const c = BOOK.multiCases.find((x) => x.id === id) || BOOK.multiCases[0];
  const [step, setStep] = useState(0);
  const [score, setScore] = useState(0);
  const [choice, setChoice] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const done = step >= c.steps.length;

  if (done) {
    const pct = Math.round(score * 100 / c.steps.length);
    return (
      <View style={{ flex: 1 }}>
        <AppHeader title="Case Lab" canBack onBack={back} colors={colors} />
        <ScrollScreen colors={colors}>
          <View style={[styles.resultCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <Text style={styles.resultEmoji}>🧭</Text>
            <Text style={[styles.resultTitle, { color: colors.text }]}>{pct}%</Text>
            <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{score}/{c.steps.length} steps</Text>
            <PressButton title={fmt(lang, 'Làm lại case', 'Restart case')} onPress={() => { setStep(0); setScore(0); setChoice(null); setFeedback(null); }} colors={colors} />
          </View>
        </ScrollScreen>
      </View>
    );
  }

  const s = c.steps[step];
  const submit = () => {
    if (choice == null) return;
    const ok = choice === s.answer;
    setFeedback(ok);
    if (ok) setScore((x) => x + 1);
  };
  const next = () => {
    const nextStep = step + 1;
    if (nextStep >= c.steps.length) {
      const pct = Math.round(score * 100 / c.steps.length);
      setState((st) => ({ ...st, caseResults: { ...st.caseResults, [c.id]: pct } }));
    }
    setStep(nextStep);
    setChoice(null);
    setFeedback(null);
  };

  return (
    <View style={{ flex: 1 }}>
      <AppHeader title={fmt(lang, c.title_vi, c.title_en)} subtitle={`${fmt(lang, 'Bước', 'Step')} ${step + 1}/${c.steps.length}`} canBack onBack={back} colors={colors} />
      <ScrollScreen colors={colors}>
        <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <View style={styles.cardBody}>
            <Text style={[styles.quizQuestion, { color: colors.text, fontSize: 20 * fontScale }]}>{fmt(lang, s.q_vi, s.q_en)}</Text>
            {s.options_vi.map((opt, i) => {
              const selected = choice === i;
              const correct = feedback != null && i === s.answer;
              const wrong = feedback === false && selected;
              return (
                <Pressable disabled={feedback != null} key={i} onPress={() => setChoice(i)} style={[styles.option, {
                  backgroundColor: correct ? colors.greenSoft : wrong ? colors.redSoft : selected ? colors.primarySoft : colors.card,
                  borderColor: correct ? colors.green : wrong ? colors.red : selected ? colors.primary : colors.line,
                }]}>
                  <Text style={[styles.optionLetter, { color: colors.primary }]}>{String.fromCharCode(65 + i)}</Text>
                  <Text style={[styles.optionText, { color: colors.text }]}>{fmt(lang, opt, s.options_en[i])}</Text>
                </Pressable>
              );
            })}
            {feedback != null && (
              <View style={[styles.feedback, { backgroundColor: feedback ? colors.greenSoft : colors.redSoft }]}>
                <Text style={{ color: feedback ? colors.green : colors.red, fontWeight: '900', marginBottom: 6 }}>{feedback ? fmt(lang, '✓ Chính xác', '✓ Correct') : fmt(lang, '✕ Chưa đúng', '✕ Not correct')}</Text>
                <BilingualBlock vi={s.why_vi} en={s.why_en} lang={lang} colors={colors} fontScale={fontScale} compact />
              </View>
            )}
            {feedback == null ? (
              <PressButton title={fmt(lang, 'Trả lời', 'Submit')} onPress={submit} disabled={choice == null} colors={colors} />
            ) : (
              <PressButton title={step + 1 === c.steps.length ? fmt(lang, 'Hoàn thành', 'Finish') : fmt(lang, 'Tiếp tục', 'Continue')} onPress={next} colors={colors} />
            )}
          </View>
        </View>
      </ScrollScreen>
    </View>
  );
}

function WorkbenchHome({ ctx }) {
  const { colors, lang, go, state } = ctx;
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>Workbench</Text>
      <Text style={[styles.pageSubtitle, { color: colors.muted }]}>{fmt(lang, 'Công cụ làm việc thật – nhập, tính, lưu và chia sẻ.', 'Practical tools – enter, calculate, save, and share.')}</Text>
      {BOOK.workbenchTemplates.map((t) => (
        <Pressable key={t.id} onPress={() => go('workbenchForm', { id: t.id })} style={[styles.featureCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <Text style={styles.featureIcon}>{t.id === 'risk' ? '⚠️' : t.id === 'decision' ? '⚖️' : t.id === '5why' ? '❓' : '🧰'}</Text>
          <View style={{ flex: 1 }}>
            <Text style={[styles.featureTitle, { color: colors.text }]}>{fmt(lang, t.name_vi, t.name_en)}</Text>
            <Text style={[styles.featureSub, { color: colors.muted }]}>{t.category}</Text>
          </View>
          {!!state.workbenchDocs[t.id] && <Text style={{ color: colors.green, fontWeight: '900' }}>✓</Text>}
          <Text style={[styles.chevron, { color: colors.muted }]}>›</Text>
        </Pressable>
      ))}
    </ScrollScreen>
  );
}

function WorkbenchForm({ ctx, id }) {
  const { colors, lang, state, setState, back, fontScale } = ctx;
  const template = BOOK.workbenchTemplates.find((x) => x.id === id) || BOOK.workbenchTemplates[0];
  const [values, setValues] = useState({ ...(state.workbenchDocs[id] || {}) });
  const [result, setResult] = useState('');

  const calculate = () => {
    if (id === 'risk') {
      const p = Number(values.probability), i = Number(values.impact), rp = Number(values.residual_p), ri = Number(values.residual_i);
      if ([p, i, rp, ri].some((x) => !Number.isFinite(x) || x < 1 || x > 5)) {
        setResult(fmt(lang, 'Hãy nhập Probability/Impact từ 1 đến 5.', 'Enter Probability/Impact from 1 to 5.'));
      } else setResult(`Initial Risk = ${p * i} (${p}×${i})  |  Residual Risk = ${rp * ri} (${rp}×${ri})`);
      return;
    }
    if (id === 'decision') {
      try {
        const options = String(values.options || '').split(',').map((x) => x.trim()).filter(Boolean);
        const weights = String(values.weights || '').split(',').map((x) => Number(x.trim())).filter((x) => Number.isFinite(x));
        const criteria = String(values.criteria || '').split(',').map((x) => x.trim()).filter(Boolean);
        const rows = String(values.scores || '').split(';').map((r) => r.trim()).filter(Boolean).map((r) => r.split(',').map((x) => Number(x.trim())));
        if (!options.length || options.length !== rows.length || criteria.length !== weights.length || rows.some((r) => r.length !== weights.length)) throw new Error();
        const totalW = weights.reduce((a, b) => a + b, 0);
        const totals = options.map((name, oi) => [name, rows[oi].reduce((sum, score, ci) => sum + score * weights[ci], 0) / totalW]);
        totals.sort((a, b) => b[1] - a[1]);
        setResult(totals.map(([n, v]) => `${n}: ${v.toFixed(2)}`).join('   |   '));
      } catch {
        setResult(fmt(lang, "Scores: mỗi phương án một hàng ngăn bằng ';'. Ví dụ 8,7,9;7,9,8", "Scores: one row per option separated by ';'. Example 8,7,9;7,9,8"));
      }
      return;
    }
    const filled = template.fields.filter(([k]) => String(values[k] || '').trim()).length;
    setResult(fmt(lang, `Đã điền ${filled}/${template.fields.length} trường. Kiểm tra logic và bằng chứng trước khi chốt.`, `${filled}/${template.fields.length} fields completed. Check logic and evidence before closing.`));
  };

  const save = () => {
    setState((s) => ({ ...s, workbenchDocs: { ...s.workbenchDocs, [id]: values } }));
    Alert.alert('Workbench', fmt(lang, 'Đã lưu offline.', 'Saved offline.'));
  };

  const share = async () => {
    const lines = [fmt(lang, template.name_vi, template.name_en), ''];
    template.fields.forEach(([k, label]) => { lines.push(label, String(values[k] || ''), ''); });
    if (result) lines.push('Result', result);
    await Share.share({ message: lines.join('\n') });
  };

  return (
    <View style={{ flex: 1 }}>
      <AppHeader title={fmt(lang, template.name_vi, template.name_en)} canBack onBack={back} colors={colors} />
      <ScrollScreen colors={colors} keyboard>
        <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <View style={styles.cardBody}>
            {template.fields.map(([key, label]) => (
              <View key={key} style={{ marginBottom: 14 }}>
                <Text style={[styles.inputLabel, { color: colors.navy }]}>{label}</Text>
                <TextInput
                  value={String(values[key] || '')}
                  onChangeText={(txt) => setValues((v) => ({ ...v, [key]: txt }))}
                  multiline
                  textAlignVertical="top"
                  placeholder="..."
                  placeholderTextColor={colors.muted}
                  style={[styles.multiInput, { backgroundColor: colors.input, borderColor: colors.line, color: colors.text, fontSize: 15 * fontScale }]}
                />
              </View>
            ))}
            {!!result && <View style={[styles.feedback, { backgroundColor: colors.primarySoft }]}><Text selectable style={[styles.bodyText, { color: colors.text, fontWeight: '800' }]}>{result}</Text></View>}
            <View style={styles.stackGap}>
              <PressButton title={fmt(lang, 'Tính / Phân tích', 'Calculate / Analyze')} onPress={calculate} colors={colors} />
              <PressButton title={fmt(lang, 'Lưu', 'Save')} onPress={save} colors={colors} kind="secondary" />
              <PressButton title={fmt(lang, 'Chia sẻ', 'Share')} onPress={share} colors={colors} kind="secondary" />
            </View>
          </View>
        </View>
      </ScrollScreen>
    </View>
  );
}

function NotesScreen({ ctx, id }) {
  const { colors, lang, state, setState, back, fontScale } = ctx;
  const lessonId = id || state.lastLesson || '1.1';
  const lesson = LESSON_BY_ID[lessonId];
  const [value, setValue] = useState(state.notes[lessonId] || '');

  const save = () => {
    setState((s) => ({ ...s, notes: { ...s.notes, [lessonId]: value } }));
    Alert.alert(fmt(lang, 'Ghi chú', 'Notes'), fmt(lang, 'Đã lưu offline.', 'Saved offline.'));
  };
  const shareAll = async () => {
    const lines = ['TƯ DUY ĐÚNG / THINK RIGHT – NOTES', ''];
    ALL_LESSONS.forEach((l) => {
      const n = state.notes[l.id];
      if (String(n || '').trim()) lines.push(`${l.id} ${l.title} / ${BOOK.enLessons[l.id].title}`, n, '');
    });
    await Share.share({ message: lines.join('\n') });
  };

  return (
    <View style={{ flex: 1 }}>
      <AppHeader title={fmt(lang, 'Ghi chú', 'Notes')} subtitle={fmt(lang, lesson.title, BOOK.enLessons[lessonId].title)} canBack onBack={back} colors={colors} />
      <ScrollScreen colors={colors} keyboard>
        <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <View style={styles.cardBody}>
            <TextInput
              value={value}
              onChangeText={setValue}
              multiline
              textAlignVertical="top"
              placeholder={fmt(lang, 'Viết điều bạn muốn nhớ...', 'Write what you want to remember...')}
              placeholderTextColor={colors.muted}
              style={[styles.noteInput, { backgroundColor: colors.input, color: colors.text, borderColor: colors.line, fontSize: 16 * fontScale }]}
            />
            <PressButton title={fmt(lang, 'Lưu ghi chú', 'Save note')} onPress={save} colors={colors} />
            <PressButton title={fmt(lang, 'Chia sẻ tất cả ghi chú', 'Share all notes')} onPress={shareAll} colors={colors} kind="secondary" />
          </View>
        </View>
      </ScrollScreen>
    </View>
  );
}

function ToolsScreen({ ctx }) {
  const { colors, lang, fontScale } = ctx;
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Thư viện công cụ', 'Tool library')}</Text>
      {BOOK.tools.map((t) => {
        const e = BOOK.enTools[t.id] || {};
        return (
          <View key={t.id} style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <View style={styles.cardBody}>
              <Text style={[styles.featureTitle, { color: colors.text }]}>{t.icon || '🧰'} {t.name}</Text>
              <Text style={[styles.heroKicker, { color: colors.purple }]}>{fmt(lang, t.category, e.category || t.category)}</Text>
              <SectionCard title="Khi nào dùng" titleEn="When to use" vi={t.when} en={e.when || ''} lang={lang} colors={colors} fontScale={fontScale} />
              <SectionCard title="Các bước" titleEn="Steps" lang={lang} colors={colors} fontScale={fontScale} tone="green">
                <BulletList vi={t.steps || []} en={e.steps || []} lang={lang} colors={colors} fontScale={fontScale} />
              </SectionCard>
            </View>
          </View>
        );
      })}
    </ScrollScreen>
  );
}

function GlossaryScreen({ ctx }) {
  const { colors, lang, fontScale } = ctx;
  const [q, setQ] = useState('');
  const keys = Object.keys(BOOK.glossary).filter((k) => {
    const s = `${k} ${BOOK.glossary[k]} ${BOOK.enGlossary[k] || ''}`.toLowerCase();
    return !q.trim() || s.includes(q.trim().toLowerCase());
  }).sort();
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Từ điển', 'Glossary')}</Text>
      <TextInput value={q} onChangeText={setQ} placeholder={fmt(lang, 'Tìm thuật ngữ...', 'Search terms...')} placeholderTextColor={colors.muted} style={[styles.searchInput, { backgroundColor: colors.input, color: colors.text, borderColor: colors.line }]} />
      {keys.map((k) => (
        <View key={k} style={[styles.card, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <View style={styles.cardBody}>
            <Text style={[styles.featureTitle, { color: colors.primary }]}>{k}</Text>
            <BilingualBlock vi={BOOK.glossary[k]} en={BOOK.enGlossary[k] || ''} lang={lang} colors={colors} fontScale={fontScale} />
          </View>
        </View>
      ))}
    </ScrollScreen>
  );
}

function ProgressScreen({ ctx }) {
  const { colors, lang, progress, state } = ctx;
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Tiến độ học tập', 'Learning progress')}</Text>
      <View style={styles.statsGrid}>
        {[
          [`${progress.read}/40`, fmt(lang, 'Đã đọc', 'Read')],
          [`${progress.quiz}/40`, 'Quiz'],
          [`${progress.quizAvg}%`, fmt(lang, 'Quiz TB', 'Quiz avg')],
          [String(progress.due), fmt(lang, 'Cần ôn', 'Due')],
          [String(progress.notes), fmt(lang, 'Ghi chú', 'Notes')],
          [String(progress.worksheets), 'Worksheets'],
        ].map(([v, label], i) => (
          <View key={i} style={[styles.statCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <Text style={[styles.statValue, { color: colors.text }]}>{v}</Text>
            <Text style={[styles.statLabel, { color: colors.muted }]}>{label}</Text>
          </View>
        ))}
      </View>
      {BOOK.chapters.map((c, ci) => {
        const ids = c.lessons.map((l) => l.id);
        const read = ids.filter((id) => state.readLessons.includes(id)).length;
        const en = BOOK.enChapters[String(ci + 1)] || {};
        return (
          <View key={ci} style={[styles.progressCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
            <Text style={[styles.chapterTitle, { color: colors.text }]}>{fmt(lang, c.title, en.title || c.title)}</Text>
            <Text style={[styles.smallNote, { color: colors.muted }]}>{read}/{ids.length}</Text>
            <View style={[styles.progressTrack, { backgroundColor: colors.line }]}>
              <View style={[styles.progressFill, { backgroundColor: colors.primary, width: `${read * 100 / ids.length}%` }]} />
            </View>
          </View>
        );
      })}
    </ScrollScreen>
  );
}

function MoreScreen({ ctx }) {
  const { colors, lang, go, state, setState, fontScale } = ctx;
  const setLang = (x) => setState((s) => ({ ...s, language: x }));
  return (
    <ScrollScreen colors={colors}>
      <Text style={[styles.pageTitle, { color: colors.text }]}>{fmt(lang, 'Thêm', 'More')}</Text>
      {[
        ['notes', '📝', 'Ghi chú', 'Notes'],
        ['tools', '🧰', 'Thư viện công cụ', 'Tool library'],
        ['glossary', '📚', 'Từ điển', 'Glossary'],
        ['progress', '📊', 'Tiến độ', 'Progress'],
        ['quizHome', '✅', 'Quiz', 'Quiz'],
        ['caseLab', '🧭', 'Case Lab', 'Case Lab'],
      ].map(([route, icon, vi, en]) => (
        <Pressable key={route} onPress={() => go(route, route === 'notes' ? { id: state.lastLesson } : {})} style={[styles.simpleRow, { backgroundColor: colors.card, borderColor: colors.line }]}>
          <Text style={styles.featureIcon}>{icon}</Text>
          <Text style={[styles.lessonRowText, { color: colors.text }]}>{fmt(lang, vi, en)}</Text>
          <Text style={[styles.chevron, { color: colors.muted }]}>›</Text>
        </Pressable>
      ))}

      <View style={[styles.settingsCard, { backgroundColor: colors.card, borderColor: colors.line }]}>
        <Text style={[styles.sectionHeading, { color: colors.text, marginTop: 0 }]}>{fmt(lang, 'Cài đặt đọc', 'Reading settings')}</Text>
        <Text style={[styles.inputLabel, { color: colors.navy }]}>{fmt(lang, 'Ngôn ngữ', 'Language')}</Text>
        <LanguagePills lang={lang} setLang={setLang} colors={colors} />
        <Text style={[styles.inputLabel, { color: colors.navy, marginTop: 18 }]}>{fmt(lang, 'Cỡ chữ', 'Text size')}</Text>
        <View style={styles.rateRow}>
          <PressButton title="A−" onPress={() => setState((s) => ({ ...s, fontScale: Math.max(0.85, Number(s.fontScale || 1) - 0.1) }))} colors={colors} kind="secondary" style={{ flex: 1 }} />
          <View style={[styles.fontValue, { borderColor: colors.line }]}><Text style={{ color: colors.text, fontWeight: '800' }}>{fontScale.toFixed(1)}×</Text></View>
          <PressButton title="A+" onPress={() => setState((s) => ({ ...s, fontScale: Math.min(1.35, Number(s.fontScale || 1) + 0.1) }))} colors={colors} kind="secondary" style={{ flex: 1 }} />
        </View>
        <Text style={[styles.inputLabel, { color: colors.navy, marginTop: 18 }]}>{fmt(lang, 'Giao diện', 'Theme')}</Text>
        <PressButton title={state.theme === 'dark' ? '☀️ Light' : '🌙 Dark'} onPress={() => setState((s) => ({ ...s, theme: s.theme === 'dark' ? 'light' : 'dark' }))} colors={colors} kind="secondary" />
      </View>
    </ScrollScreen>
  );
}

function ScreenRouter({ ctx }) {
  const { screen } = ctx;
  if (screen.name === 'home') return <HomeScreen ctx={ctx} />;
  if (screen.name === 'library') return <LibraryScreen ctx={ctx} />;
  if (screen.name === 'lesson') return <LessonScreen ctx={ctx} id={screen.params.id} />;
  if (screen.name === 'quizHome') return <QuizHome ctx={ctx} />;
  if (screen.name === 'quiz') return <QuizScreen ctx={ctx} id={screen.params.id} />;
  if (screen.name === 'review') return <ReviewScreen ctx={ctx} />;
  if (screen.name === 'caseLab') return <CaseLabHome ctx={ctx} />;
  if (screen.name === 'caseRun') return <CaseRun ctx={ctx} id={screen.params.id} />;
  if (screen.name === 'workbench') return <WorkbenchHome ctx={ctx} />;
  if (screen.name === 'workbenchForm') return <WorkbenchForm ctx={ctx} id={screen.params.id} />;
  if (screen.name === 'notes') return <NotesScreen ctx={ctx} id={screen.params.id} />;
  if (screen.name === 'tools') return <ToolsScreen ctx={ctx} />;
  if (screen.name === 'glossary') return <GlossaryScreen ctx={ctx} />;
  if (screen.name === 'progress') return <ProgressScreen ctx={ctx} />;
  return <MoreScreen ctx={ctx} />;
}

function MainApp() {
  const [state, setState] = useState(DEFAULT_STATE);
  const [loaded, setLoaded] = useState(false);
  const [screen, setScreen] = useState({ name: 'home', params: {} });
  const [history, setHistory] = useState([]);
  const [focus, setFocus] = useState(false);

  const lang = state.language || 'BI';
  const colors = COLORS[state.theme === 'dark' ? 'dark' : 'light'];
  const fontScale = Number(state.fontScale || 1);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((raw) => {
      if (raw) {
        try {
          const parsed = JSON.parse(raw);
          setState({ ...DEFAULT_STATE, ...parsed });
        } catch {}
      }
      setLoaded(true);
    });
  }, []);

  useEffect(() => {
    if (!loaded) return;
    const timer = setTimeout(() => AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(state)), 300);
    return () => clearTimeout(timer);
  }, [state, loaded]);

  const go = (name, params = {}, replace = false) => {
    setFocus(false);
    if (!replace) setHistory((h) => [...h, screen]);
    setScreen({ name, params });
  };

  const goRoot = (name) => {
    setFocus(false);
    setHistory([]);
    setScreen({ name, params: {} });
  };

  const back = () => {
    setFocus(false);
    setHistory((h) => {
      if (!h.length) {
        setScreen({ name: 'home', params: {} });
        return [];
      }
      const prev = h[h.length - 1];
      setScreen(prev);
      return h.slice(0, -1);
    });
  };

  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (screen.name !== 'home' || history.length) {
        back();
        return true;
      }
      Alert.alert(
        fmt(lang, 'Thoát ứng dụng?', 'Exit app?'),
        fmt(lang, 'Bạn có muốn thoát Tư Duy Đúng?', 'Do you want to exit Think Right?'),
        [
          { text: fmt(lang, 'Không', 'Cancel'), style: 'cancel' },
          { text: fmt(lang, 'Thoát', 'Exit'), onPress: () => BackHandler.exitApp() },
        ],
      );
      return true;
    });
    return () => sub.remove();
  }, [screen, history, lang]);

  const pan = useMemo(() => PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => screen.name !== 'home' && g.x0 < 28 && g.dx > 12 && Math.abs(g.dx) > Math.abs(g.dy) * 1.4,
    onPanResponderRelease: (_, g) => { if (g.dx > 85) back(); },
  }), [screen, history]);

  const progress = useMemo(() => {
    const scores = Object.values(state.quizScores || {}).map(Number).filter(Number.isFinite);
    return {
      read: state.readLessons.length,
      quiz: Object.keys(state.quizScores || {}).length,
      quizAvg: scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0,
      due: ALL_LESSONS.filter((l) => !state.reviewState[l.id] || (state.reviewState[l.id].due || todayISO()) <= todayISO()).length,
      notes: Object.values(state.notes || {}).filter((x) => String(x || '').trim()).length,
      worksheets: Object.values(state.workbenchDocs || {}).filter(Boolean).length,
    };
  }, [state]);

  if (!loaded) {
    return (
      <SafeAreaView style={[styles.loading, { backgroundColor: COLORS.light.bg }]} edges={['top', 'bottom']}>
        <Text style={{ fontSize: 24, fontWeight: '900', color: COLORS.light.navy }}>TƯ DUY ĐÚNG</Text>
        <Text style={{ marginTop: 8, color: COLORS.light.muted }}>THINK RIGHT • MOBILE V1.0</Text>
      </SafeAreaView>
    );
  }

  const ctx = { state, setState, colors, lang, screen, go, goRoot, back, progress, fontScale, focus, setFocus };
  const hideBottom = focus || ['quiz', 'caseRun', 'workbenchForm', 'notes'].includes(screen.name);

  return (
    <SafeAreaView style={[styles.safe, { backgroundColor: colors.bg }]} edges={['top', 'left', 'right']}>
      <StatusBar barStyle={state.theme === 'dark' ? 'light-content' : 'dark-content'} backgroundColor={colors.card} />
      <View style={{ flex: 1 }} {...pan.panHandlers}>
        {!focus && (
          <View style={[styles.brandBar, { backgroundColor: colors.card, borderBottomColor: colors.line }]}>
            <View style={{ flex: 1 }}>
              <Text style={[styles.brand, { color: colors.navy }]}>TƯ DUY ĐÚNG</Text>
              <Text style={[styles.brandSub, { color: colors.muted }]}>THINK RIGHT • MOBILE V1.0</Text>
            </View>
            <LanguagePills lang={lang} setLang={(x) => setState((s) => ({ ...s, language: x }))} colors={colors} />
          </View>
        )}
        <View style={{ flex: 1 }}>
          <ScreenRouter ctx={ctx} />
        </View>
        <BottomNav screen={screen} goRoot={goRoot} colors={colors} hidden={hideBottom} />
      </View>
    </SafeAreaView>
  );
}

export default function App() {
  return <SafeAreaProvider><MainApp /></SafeAreaProvider>;
}

const styles = StyleSheet.create({
  safe: { flex: 1 },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  brandBar: { minHeight: 62, borderBottomWidth: StyleSheet.hairlineWidth, paddingHorizontal: 14, paddingVertical: 8, flexDirection: 'row', alignItems: 'center', gap: 10 },
  brand: { fontSize: 20, fontWeight: '900', letterSpacing: 0.2 },
  brandSub: { fontSize: 10, fontWeight: '700', marginTop: 1 },
  segment: { flexDirection: 'row', borderWidth: 1, borderRadius: 12, padding: 2 },
  segmentItem: { minWidth: 38, minHeight: 34, paddingHorizontal: 8, alignItems: 'center', justifyContent: 'center', borderRadius: 9 },
  header: { borderBottomWidth: StyleSheet.hairlineWidth, minHeight: 58, justifyContent: 'center' },
  headerRow: { flexDirection: 'row', alignItems: 'center', minHeight: 58 },
  iconButton: { width: 52, minHeight: 52, justifyContent: 'center', alignItems: 'center' },
  backGlyph: { fontSize: 38, lineHeight: 40, fontWeight: '300' },
  headerCenter: { flex: 1, minWidth: 0 },
  headerTitle: { fontSize: 16, fontWeight: '900' },
  headerSubtitle: { fontSize: 11, marginTop: 2 },
  headerRight: { width: 52, alignItems: 'center' },
  scrollContent: { padding: 12, paddingBottom: 120 },
  button: { minHeight: 48, borderWidth: 1, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 11, justifyContent: 'center', alignItems: 'center', marginVertical: 4 },
  buttonText: { fontSize: 14, fontWeight: '900', textAlign: 'center' },
  bottomNav: { borderTopWidth: StyleSheet.hairlineWidth, flexDirection: 'row', paddingTop: 4 },
  navItem: { flex: 1, minHeight: 56, alignItems: 'center', justifyContent: 'center' },
  navIcon: { fontSize: 21, fontWeight: '800' },
  navLabel: { fontSize: 10, fontWeight: '800', marginTop: 2 },
  hero: { borderWidth: 1, borderRadius: 18, padding: 18, marginBottom: 12 },
  heroKicker: { fontSize: 11, fontWeight: '900', letterSpacing: 0.4 },
  heroTitle: { fontSize: 32, fontWeight: '900', marginTop: 6 },
  heroText: { fontSize: 16, lineHeight: 23, marginTop: 5 },
  heroActions: { flexDirection: 'row', gap: 8, marginTop: 14 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 8 },
  statCard: { width: '48.6%', borderWidth: 1, borderRadius: 14, padding: 14 },
  statValue: { fontSize: 26, fontWeight: '900' },
  statLabel: { fontSize: 12, fontWeight: '700', marginTop: 3 },
  sectionHeading: { fontSize: 20, fontWeight: '900', marginTop: 14, marginBottom: 8 },
  featureCard: { flexDirection: 'row', alignItems: 'center', gap: 12, borderWidth: 1, borderRadius: 14, padding: 14, marginBottom: 9, minHeight: 82 },
  featureIcon: { fontSize: 26 },
  featureTitle: { fontSize: 16, fontWeight: '900' },
  featureSub: { fontSize: 13, lineHeight: 19, marginTop: 3 },
  chevron: { fontSize: 28, fontWeight: '300' },
  pageTitle: { fontSize: 28, fontWeight: '900', marginBottom: 6 },
  pageSubtitle: { fontSize: 14, lineHeight: 21, marginBottom: 14 },
  searchInput: { minHeight: 50, borderWidth: 1, borderRadius: 12, paddingHorizontal: 14, fontSize: 16, marginBottom: 12 },
  chapterCard: { flexDirection: 'row', gap: 12, borderWidth: 1, borderRadius: 16, padding: 14, marginBottom: 10 },
  chapterNumber: { fontSize: 24, fontWeight: '900', width: 38 },
  chapterTitle: { fontSize: 16, fontWeight: '900' },
  chapterSub: { fontSize: 12, lineHeight: 18, marginTop: 3 },
  lessonRow: { flexDirection: 'row', alignItems: 'center', minHeight: 54, borderTopWidth: StyleSheet.hairlineWidth, paddingVertical: 8, gap: 7 },
  lessonId: { width: 46, fontSize: 12, fontWeight: '900' },
  lessonRowText: { flex: 1, fontSize: 14, lineHeight: 20, fontWeight: '700' },
  lessonHero: { borderWidth: 1, borderRadius: 16, padding: 16, marginBottom: 10 },
  lessonTitle: { fontWeight: '900', lineHeight: 34 },
  lessonSummary: { lineHeight: 23, marginTop: 8 },
  lessonActions: { flexDirection: 'row', gap: 6, marginTop: 14 },
  card: { borderWidth: 1, borderRadius: 14, overflow: 'hidden', marginBottom: 10 },
  cardTitleBar: { paddingHorizontal: 14, paddingVertical: 10 },
  cardTitle: { fontSize: 16, fontWeight: '900' },
  cardBody: { padding: 14 },
  bodyText: { fontSize: 16, lineHeight: 24 },
  langBadge: { fontSize: 10, fontWeight: '900', letterSpacing: 0.3, marginBottom: 5 },
  divider: { height: StyleSheet.hairlineWidth, marginVertical: 12 },
  bulletRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 7 },
  bulletDot: { width: 18, fontSize: 18, lineHeight: 24, fontWeight: '900' },
  memoryStep: { flexDirection: 'row', gap: 10, padding: 12, borderWidth: 1, borderRadius: 12, marginBottom: 8 },
  memoryIndex: { width: 28, fontWeight: '900', fontSize: 13 },
  memoryTitle: { fontSize: 15, fontWeight: '900', marginBottom: 6 },
  storyTitle: { fontSize: 19, fontWeight: '900', marginBottom: 10 },
  takeaway: { borderWidth: 1, borderRadius: 12, padding: 12, marginTop: 12 },
  prevNextRow: { flexDirection: 'row', gap: 8, marginTop: 4 },
  focusBar: { minHeight: 48, borderBottomWidth: StyleSheet.hairlineWidth, paddingHorizontal: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  focusExit: { minHeight: 48, justifyContent: 'center' },
  simpleRow: { minHeight: 62, borderWidth: 1, borderRadius: 12, flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 12, marginBottom: 8 },
  quizProgress: { height: 7, borderRadius: 7, overflow: 'hidden', marginBottom: 12 },
  quizProgressFill: { height: 7 },
  quizQuestion: { fontWeight: '900', lineHeight: 28, marginBottom: 14 },
  option: { minHeight: 58, borderWidth: 1.5, borderRadius: 12, padding: 12, flexDirection: 'row', alignItems: 'flex-start', marginBottom: 9, gap: 10 },
  optionLetter: { width: 24, fontWeight: '900', fontSize: 16 },
  optionText: { flex: 1, lineHeight: 22, fontWeight: '600' },
  feedback: { borderRadius: 12, padding: 12, marginVertical: 10 },
  resultCard: { borderWidth: 1, borderRadius: 18, padding: 22, alignItems: 'center' },
  resultEmoji: { fontSize: 54 },
  resultTitle: { fontSize: 46, fontWeight: '900', marginVertical: 8 },
  flashCard: { borderWidth: 1, borderRadius: 18, padding: 20 },
  flashFront: { fontWeight: '900', lineHeight: 36, marginTop: 8, marginBottom: 12 },
  rateRow: { flexDirection: 'row', gap: 7, marginTop: 14, alignItems: 'center' },
  smallNote: { fontSize: 12, lineHeight: 18, marginTop: 8 },
  inputLabel: { fontSize: 12, fontWeight: '900', marginBottom: 6 },
  multiInput: { minHeight: 76, borderWidth: 1, borderRadius: 10, padding: 10, lineHeight: 21 },
  noteInput: { minHeight: 320, borderWidth: 1, borderRadius: 12, padding: 12, lineHeight: 23, marginBottom: 12 },
  stackGap: { marginTop: 6 },
  progressCard: { borderWidth: 1, borderRadius: 12, padding: 12, marginBottom: 8 },
  progressTrack: { height: 8, borderRadius: 8, overflow: 'hidden', marginTop: 8 },
  progressFill: { height: 8 },
  settingsCard: { borderWidth: 1, borderRadius: 16, padding: 14, marginTop: 14 },
  fontValue: { minHeight: 48, minWidth: 70, borderWidth: 1, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
});
