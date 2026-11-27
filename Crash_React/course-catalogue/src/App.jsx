// src/App.jsx
import Header from './components/Header.jsx';
import Section from './components/Section.jsx';
import CourseList from './components/CourseList.jsx';
import Footer from './components/Footer.jsx';
import courses from './data/courses.js';
import './App.css';

export default function App() {
  const featuredCourses = courses.filter((course) => course.featured);
  const openCount = courses.filter((course) => course.seatsLeft > 0).length;

  return (
    <div className="container">
      <Header
        title="Course Catalogue"
        subtitle={`${openCount} of ${courses.length} courses are open for enrolment`}
      />

      <main>
        <Section heading="Featured Courses">
          <CourseList courses={featuredCourses} />
        </Section>

        <Section heading="All Courses">
          <CourseList courses={courses} />
        </Section>
      </main>

      <Footer />
    </div>
  );
}