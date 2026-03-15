require('dotenv').config();
const bcrypt = require('bcryptjs');
const { connectToDatabase } = require('./config/db');
const User = require('./models/User');
const Issue = require('./models/Issue');
const SocialLink = require('./models/SocialLink');
const ContentItem = require('./models/ContentItem');
const Submission = require('./models/Submission');
const PageSetting = require('./models/PageSetting');
const { getDefaultSiteSettings } = require('./config/siteDefaults');

async function seed() {
  await connectToDatabase();

  await Promise.all([
    User.deleteMany({}),
    Issue.deleteMany({}),
    SocialLink.deleteMany({}),
    ContentItem.deleteMany({}),
    Submission.deleteMany({}),
    PageSetting.deleteMany({})
  ]);

  const email = (process.env.ADMIN_EMAIL || 'admin@example.com').trim().toLowerCase();
  const password = process.env.ADMIN_PASSWORD || 'change-this-admin-password';
  const passwordHash = await bcrypt.hash(password, 10);

  await User.create({ email, passwordHash, role: 'admin' });

  await PageSetting.insertMany([
    {
      key: 'site',
      value: getDefaultSiteSettings()
    },
    {
      key: 'about',
      value: {
        title: 'About Ultraviolet',
        body: 'Ultraviolet is a student-run creative magazine devoted to prose, poetry, art, photography, graphics, music, spoken word, and moving image. We promote creative work on and off campus and make room for experimentation across media.',
        imageUrl: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=900&q=80'
      }
    }
  ]);


  await Issue.insertMany([
    {
      year: 2025,
      title: 'Ultraviolet 2025',
      summary: 'A new issue featuring visual art, poetry, sound, and moving image.',
      coverImageUrl: 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80',
      externalUrl: getDefaultSiteSettings().issuesArchiveUrl,
      isFeatured: true,
      order: 1
    },
    {
      year: 2024,
      title: 'Ultraviolet 2024',
      summary: 'A previous issue archive entry.',
      coverImageUrl: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80',
      externalUrl: getDefaultSiteSettings().issuesArchiveUrl,
      isFeatured: true,
      order: 2
    },
    {
      year: 2023,
      title: 'Ultraviolet 2023',
      summary: 'Archive issue with student work across media.',
      coverImageUrl: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80',
      externalUrl: getDefaultSiteSettings().issuesArchiveUrl,
      isFeatured: true,
      order: 3
    }
  ]);

  await ContentItem.insertMany([
    {
      title: 'Lavender Windows',
      slug: 'lavender-windows',
      category: 'look',
      subtype: 'photography',
      creatorName: 'Maya Chen',
      summary: 'A photographic series on reflection, shadow, and evening color.',
      coverImageUrl: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
      imageUrls: [
        'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1493246318656-5bfd4cfb29b8?auto=format&fit=crop&w=1200&q=80'
      ],
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 1
    },
    {
      title: 'After the Rain',
      slug: 'after-the-rain',
      category: 'read',
      subtype: 'poem',
      creatorName: 'Leah Morgan',
      summary: 'A poem about wet streets, memory, and return.',
      body: 'The rain has ended but the city still remembers. Pavement holds the sky in fragments, and every step feels like walking through a delayed reflection. This sample text stands in for a full poem or short prose piece.',
      coverImageUrl: 'https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 2
    },
    {
      title: 'Station Voice',
      slug: 'station-voice',
      category: 'listen',
      subtype: 'spoken-word',
      creatorName: 'Jordan Patel',
      summary: 'A spoken word piece on transit, waiting, and city rhythm.',
      audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
      durationLabel: '3:42',
      coverImageUrl: 'https://images.unsplash.com/photo-1487180144351-b8472da7d491?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 3
    },
    {
      title: 'Quiet Neon',
      slug: 'quiet-neon',
      category: 'watch',
      subtype: 'short-film',
      creatorName: 'Aria Williams',
      summary: 'A short film about color, motion, and nighttime solitude.',
      videoUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      coverImageUrl: 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2025,
      isPublished: true,
      isFeatured: true,
      sortOrder: 4
    },
    {
      title: 'Glass Study No. 2',
      slug: 'glass-study-no-2',
      category: 'look',
      subtype: 'artwork',
      creatorName: 'Nina Alvarez',
      summary: 'Mixed-media digital artwork with translucent layers and soft geometry.',
      coverImageUrl: 'https://images.unsplash.com/photo-1515405295579-ba7b45403062?auto=format&fit=crop&w=1000&q=80',
      imageUrls: ['https://images.unsplash.com/photo-1515405295579-ba7b45403062?auto=format&fit=crop&w=1000&q=80'],
      issueYear: 2024,
      isPublished: true,
      sortOrder: 5
    },
    {
      title: 'North Hall, 2 A.M.',
      slug: 'north-hall-2-am',
      category: 'read',
      subtype: 'short-story',
      creatorName: 'Evan Brooks',
      summary: 'A short story about campus quiet, fluorescent light, and unplanned conversation.',
      body: 'At two in the morning, the residence hallway stopped pretending to be temporary. Doors looked permanent. The vending machine sounded like weather. Then someone at the far end laughed, and the place became human again.',
      coverImageUrl: 'https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?auto=format&fit=crop&w=1000&q=80',
      issueYear: 2024,
      isPublished: true,
      sortOrder: 6
    }
  ]);

  await Submission.insertMany([
    {
      name: 'Sample Submitter',
      email: 'submitter@example.com',
      category: 'read',
      title: 'Draft Piece',
      creatorName: 'Sample Submitter',
      summary: 'Example submission waiting for review.',
      assetUrl: 'https://example.com/draft-piece',
      notes: 'Please consider this for the next issue.',
      status: 'new'
    }
  ]);

  console.log('Database seeded successfully');
  process.exit(0);
}

seed().catch((error) => {
  console.error(error);
  process.exit(1);
});
