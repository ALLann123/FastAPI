import Badge from "./Badge";

function SeatStatus({seatsLeft}){
    if(seatsLeft===0){
        return <Badge text="Full" type="danger"/>
    }
    if (seatsLeft<=5){
        return <Badge text={`Only ${seatsLeft} left`} type="warning"/>;
    }
    return <Badge text="Open" type="success"/>;
}

export default function CourseCard({course}){
    //destructing
    const {title, instructor, level, hours, price, seatsLeft, featured}=course;

    return (
        <article className={`card ${seatsLeft===0 ? 'card-full':''}`}>
            <div className="badges">
                <Badge text={level}/>
                <SeatStatus seatsLeft={seatsLeft}/>
            </div>
            <h3>
                {featured && <span aria-label="Featured">⭐</span>}
                {title}
            </h3>
            <p>Instructor: {instructor}</p>
            <p>{hours} hours</p>
            <p className="price">
                {price===0?'Free':`Ksh ${price.toLocaleString()}`}
            </p>
        </article>
    )
}