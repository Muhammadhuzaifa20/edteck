# Lesson Planner AI - Frontend

A modern, interactive Next.js frontend for an AI-powered lesson planning system. This application provides an intuitive interface for educators to create personalized lesson plans based on student profiles and AI recommendations.

## 🚀 Features

### ✨ Interactive User Experience
- **Multi-step workflow** with progress tracking
- **Smooth animations** using Framer Motion
- **Responsive design** that works on all devices
- **Real-time progress updates** and visual feedback

### 🎯 Core Functionality
1. **Student Input** - Collect comprehensive student information
2. **AI Template Selection** - Get intelligent recommendations for lesson templates
3. **Lesson Planning** - Customize and organize lesson stages
4. **Activity Management** - Configure detailed activities for each stage
5. **Progress Tracking** - Visual analytics and completion status

### 📊 Data Visualization
- **Progress charts** showing completion status
- **Activity distribution** graphs
- **Stage completion** tracking
- **Real-time statistics** and metrics

## 🛠️ Technology Stack

- **Frontend Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS for responsive design
- **Animations**: Framer Motion for smooth transitions
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React for consistent iconography
- **State Management**: React hooks for local state

## 📁 Project Structure

```
src/
├── app/
│   ├── page.tsx              # Main application component
│   ├── layout.tsx            # Root layout with metadata
│   └── globals.css           # Global styles
├── components/
│   ├── StudentInput.tsx      # Student information form
│   ├── TemplateRecommendation.tsx  # AI template selection
│   ├── LessonPlanning.tsx    # Stage customization
│   ├── ActivityManager.tsx   # Activity configuration
│   └── ProgressTracker.tsx   # Progress visualization
└── types/                    # TypeScript type definitions
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lesson-planner-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
npm run build
npm start
```

## 🎨 Usage Guide

### 1. Student Information Input
- Enter student's basic details (name, grade, subject)
- Select learning style (visual, auditory, kinesthetic, reading/writing)
- Describe interests, strengths, and areas for growth
- All fields are validated before proceeding

### 2. Template Selection
- View AI-powered template recommendations
- See confidence scores and rationale for each template
- Choose from 5E, 7E, PBL, or Dynamic models
- Explore detailed information about each template

### 3. Lesson Planning
- Customize lesson stages and their sequence
- Add, remove, or reorder stages as needed
- Each stage includes estimated duration and learning objectives
- Real-time preview of lesson structure

### 4. Activity Management
- Configure activities for each lesson stage
- Choose from predefined activity types or create custom ones
- Set duration, materials, and adaptations
- Navigate between stages to manage all activities

### 5. Progress Tracking
- Monitor overall completion status
- View detailed analytics and statistics
- Track stage-by-stage progress
- Export or review completed lesson plans

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=Lesson Planner AI
```

### Customization
- **Colors**: Modify Tailwind CSS configuration in `tailwind.config.js`
- **Animations**: Adjust Framer Motion settings in component files
- **Charts**: Customize Recharts configurations in `ProgressTracker.tsx`

## 📱 Responsive Design

The application is fully responsive and optimized for:
- **Desktop**: Full-featured experience with side-by-side layouts
- **Tablet**: Adaptive layouts with touch-friendly interactions
- **Mobile**: Streamlined single-column layouts for small screens

## 🎯 Key Components

### StudentInput
- Comprehensive form validation
- Dynamic field updates
- Responsive grid layouts
- Error handling and user feedback

### TemplateRecommendation
- AI recommendation display
- Confidence scoring visualization
- Interactive template selection
- Detailed rationale explanations

### LessonPlanning
- Drag-and-drop stage management
- Real-time stage customization
- Progress indicators
- Validation and error handling

### ActivityManager
- Stage-by-stage navigation
- Activity CRUD operations
- Material and adaptation management
- Progress tracking per stage

### ProgressTracker
- Real-time statistics
- Interactive charts and graphs
- Stage completion visualization
- Next steps guidance

## 🔌 API Integration

The frontend is designed to integrate with the Python backend:

- **Student Context**: `POST /api/context`
- **Template Recommendations**: `POST /api/template/recommend`
- **Template Details**: `GET /api/templates/{name}`
- **Activity Proposals**: `POST /api/activities/propose`

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## 📦 Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Docker
```bash
docker build -t lesson-planner-frontend .
docker run -p 3000:3000 lesson-planner-frontend
```

### Static Export
```bash
npm run export
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Next.js Team** for the amazing framework
- **Tailwind CSS** for the utility-first CSS framework
- **Framer Motion** for smooth animations
- **Recharts** for beautiful data visualizations
- **Lucide** for the comprehensive icon set

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for educators and learners worldwide**
