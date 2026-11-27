import CourseCard from "./CourseCard";

export default function CourseList({courses}){
    if(courses.length===0){
        return <p>No courses to show</p>;
    }

    return(
        <div className="grid">
            {courses.map((course)=>(
                <CourseCard key={course.id} course={course}/>
            ))}
        </div>
    );
}