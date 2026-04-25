export interface Question {
  question_number: number | null;
  question_title: string | null;
  student_answer: string | null;
  correct_answer: string;
  marks: number | null;
  score: number;
  status: string;
}

export interface Summary {
  total_score: number;
  max_score: number;
  percentage: number;
  strengths: string;
  weaknesses: string;
}

export interface Result {
  evaluation: Question[];
  summary: Summary;
}