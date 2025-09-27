# Avaire - Fashion AI Platform

A personalized fashion recommendation and virtual try-on platform for Gen Z women in India.

## 🎯 Key Features

- **Personalized Recommendations**: AI-driven outfit suggestions based on skin tone, body type, and style preferences
- **Virtual Try-On**: Advanced ML pipeline for realistic garment visualization
- **Style DNA**: Comprehensive user profiling for better personalization
- **Contextual Styling**: Recommendations for specific occasions and contexts

## 🏛️ Architecture

```
avaire/
├── frontend/          # Next.js React application
├── backend/           # FastAPI Python backend
├── ml/               # AI/ML models and pipelines
├── storage/          # Local file storage
├── data/             # Database initialization and sample data
└── docker-compose.yml # Container orchestration
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Running with Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd avaire
```

2. Start all services:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

Run `npm run lint` to validate the TypeScript + Tailwind setup after making changes. The frontend ships with sample data and will call the FastAPI backend once `NEXT_PUBLIC_API_URL` is configured.

## 📦 Technology Stack

### Frontend
- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **State Management**: React Context + hooks

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **File Storage**: Local filesystem with optional S3 replication

### AI/ML
- **Computer Vision**: PyTorch, OpenCV
- **Virtual Try-On**: Custom TPS warping + diffusion models
- **Recommendation Engine**: Rule-based + collaborative filtering
- **Image Processing**: rembg, MediaPipe, HuggingFace models

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/onboard_style_dna` - Save user style preferences
- `GET /api/catalog` - Fetch product catalog with filters
- `GET /api/recommend/{user_id}` - Get personalized recommendations
- `POST /api/tryon` - Virtual try-on processing
- `GET /api/users/{user_id}/profile` - User profile and history

### ML Endpoints
- `POST /api/ml/preprocess` - Image preprocessing pipeline
- `POST /api/ml/segment` - Human parsing and segmentation
- `POST /api/ml/warp` - Garment warping and alignment

## 📊 Database Schema

### Key Tables
- `users` - User profiles and authentication
- `style_dna` - User style preferences and measurements
- `outfits` - Product catalog with tags and metadata
- `recommendations` - Recommendation history and feedback
- `tryon_history` - Virtual try-on sessions and results

## 🎨 UI Components

### Core Components
- **Navbar**: Navigation with logo and main sections
- **OutfitCarousel**: Jordan-style product showcase
- **StyleDNAForm**: Comprehensive onboarding flow
- **FilterPanel**: Category and style filtering
- **TryOnStudio**: Virtual try-on interface
- **ProfileDashboard**: User preferences and history
- **CatalogShowcase**: Pairs filters with personalized recommendations

## 🗃️ Storage Backends

The virtual try-on pipeline persists uploads and generated renders via a pluggable storage client (`backend/services/storage.py`).

### Local Mode (default)

Files are written under the `storage/` directory and automatically served at `http://localhost:8000/storage/**`.

### S3 Mode

Set the following environment variables to mirror assets to Amazon S3:

```env
STORAGE_BACKEND=s3
S3_BUCKET_NAME=your-bucket
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
# Optional custom domain/CDN
STORAGE_PUBLIC_URL=https://cdn.your-domain.com
```

The backend writes to disk first (to feed the ML pipeline) and then uploads to S3 with `public-read` ACL so the frontend can load the resulting image immediately.

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests  
cd frontend
npm test

# ML pipeline tests
cd ml
python -m pytest tests/
```

## 🚀 Deployment

### Production Deployment
1. Update environment variables in `docker-compose.prod.yml`
2. Configure AWS S3 for file storage
3. Set up PostgreSQL RDS instance
4. Deploy using Docker Swarm or Kubernetes

### Environment Variables
```env
# Backend
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-production-secret-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
S3_BUCKET_NAME=your-s3-bucket

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 📈 Roadmap

### MVP Phase (Current)
- [x] Basic project structure
- [ ] Style DNA onboarding
- [ ] Product catalog management
- [ ] Virtual try-on pipeline
- [ ] Recommendation engine

### Phase 2
- [ ] User authentication and profiles
- [ ] Advanced ML models (diffusion-based try-on)
- [ ] Social features and sharing
- [ ] Mobile app (React Native)

### Phase 3
- [ ] Brand partner dashboard
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Expansion to men's fashion

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

Built with ❤️ by the Avaire team for Gen Z fashion enthusiasts in India.

---

**Note**: This is an MVP version focused on validating core concepts. The platform is designed to scale with advanced AI/ML capabilities and expanded catalog integration.