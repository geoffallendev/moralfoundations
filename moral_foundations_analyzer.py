"""
Moral Foundations LLM Analyzer
Analyzes multiple LLMs using the Moral Foundations Questionnaire (MFQ-30)
"""

import os
import csv
import json
import glob
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import pandas as pd

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from generate_html_report import HTMLReportGenerator

# Load environment variables
load_dotenv()


class MoralFoundationsAnalyzer:
    """Analyzes LLM responses to Moral Foundations questions"""

    def __init__(self, csv_path: str = "moralfoundations30-dataset.csv"):
        self.csv_path = csv_path
        self.questions = []
        self.part1_prompt = self._load_prompt("moral_foundations_part1_prompt")
        self.part2_prompt = self._load_prompt("moral_foundations_part2_prompt")
        self.results = []

        # Initialize LLMs
        self.llms = self._initialize_llms()

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file"""
        with open(filename, 'r') as f:
            return f.read().strip()

    def _initialize_llms(self) -> Dict[str, Any]:
        """Initialize multiple LLM instances"""
        llms = {}

        # OpenAI GPT models
        if os.getenv("OPENAI_API_KEY"):
            llms["gpt-4"] = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            llms["gpt-3.5-turbo"] = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=os.getenv("OPENAI_API_KEY")
            )

        # Anthropic Claude models
        if os.getenv("ANTHROPIC_API_KEY"):
            llms["claude-sonnet-4"] = ChatAnthropic(
                model="claude-sonnet-4-20250514",
                temperature=0.7,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ) 
            """ llms["claude-3-sonnet"] = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=0.7,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ) """

        # Google Gemini models
        if os.getenv("GOOGLE_API_KEY"):
            llms["gemini-2.5-pro"] = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro",
                temperature=0.7,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )

        if not llms:
            raise ValueError("No API keys found. Please set at least one API key in .env file")

        return llms

    def load_questions(self):
        """Load questions from CSV file"""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean up the question text (remove extra newlines)
                question_text = row['Question'].replace('\n', ' ').strip()
                self.questions.append({
                    'question': question_text,
                    'part': int(row['Part']),
                    'moral_foundation': row['Moral'],
                    'expected_output': row['Outputs']
                })

        print(f"Loaded {len(self.questions)} questions from {self.csv_path}")
        return self.questions

    def _create_prompt(self, question: Dict[str, Any]) -> List[Any]:
        """Create prompt messages based on question part"""
        if question['part'] == 1:
            system_prompt = self.part1_prompt
        else:  # part == 2
            system_prompt = self.part2_prompt

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question['question'])
        ]

        return messages

    def _extract_numeric_value(self, response: str) -> int:
        """Extract numeric value (0-5) from LLM response"""
        # Try to find a number between 0 and 5 in the response
        import re

        # First, try to find explicit ratings
        patterns = [
            r'\b([0-5])\b',  # Single digit 0-5
            r'rating[:\s]+([0-5])',  # "rating: X" or "rating X"
            r'score[:\s]+([0-5])',   # "score: X" or "score X"
            r'value[:\s]+([0-5])',   # "value: X" or "value X"
        ]

        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                return int(match.group(1))

        # If no clear number found, return -1 to indicate parsing failure
        return -1

    def query_llm(self, llm_name: str, llm: Any, question: Dict[str, Any]) -> Dict[str, Any]:
        """Query a single LLM with a question"""
        messages = self._create_prompt(question)

        try:
            response = llm.invoke(messages)
            response_text = response.content
            numeric_value = self._extract_numeric_value(response_text)

            result = {
                'llm': llm_name,
                'question': question['question'],
                'part': question['part'],
                'moral_foundation': question['moral_foundation'],
                'response': response_text,
                'extracted_value': numeric_value,
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            print(f"Error querying {llm_name}: {str(e)}")
            return {
                'llm': llm_name,
                'question': question['question'],
                'part': question['part'],
                'moral_foundation': question['moral_foundation'],
                'response': f"ERROR: {str(e)}",
                'extracted_value': -1,
                'timestamp': datetime.now().isoformat()
            }

    def analyze_all(self, limit: int = None):
        """Analyze all questions with all available LLMs"""
        questions_to_analyze = self.questions[:limit] if limit else self.questions
        total_queries = len(questions_to_analyze) * len(self.llms)

        print(f"\nStarting analysis:")
        print(f"- Questions: {len(questions_to_analyze)}")
        print(f"- LLMs: {len(self.llms)} ({', '.join(self.llms.keys())})")
        print(f"- Total queries: {total_queries}")
        print()

        query_count = 0
        for idx, question in enumerate(questions_to_analyze, 1):
            print(f"\n[Question {idx}/{len(questions_to_analyze)}] Part {question['part']}: {question['question'][:80]}...")

            for llm_name, llm in self.llms.items():
                query_count += 1
                print(f"  [{query_count}/{total_queries}] Querying {llm_name}...", end=" ")

                result = self.query_llm(llm_name, llm, question)
                self.results.append(result)

                if result['extracted_value'] != -1:
                    print(f"✓ Response: {result['extracted_value']}")
                else:
                    print(f"⚠ Could not extract value: {result['response'][:50]}...")

        print(f"\n✓ Analysis complete! {len(self.results)} total responses collected.")
        return self.results

    def save_results(self, output_dir: str = "results"):
        """Save results to JSON and CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed JSON
        json_path = os.path.join(output_dir, f"moral_foundations_results_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Saved detailed results to {json_path}")

        # Save CSV summary
        csv_path = os.path.join(output_dir, f"moral_foundations_results_{timestamp}.csv")
        df = pd.DataFrame(self.results)
        df.to_csv(csv_path, index=False)
        print(f"✓ Saved CSV summary to {csv_path}")

        # Generate analysis summary
        summary_path = self._generate_summary(output_dir, timestamp)

        # Generate HTML report
        html_generator = HTMLReportGenerator(json_path, summary_path)
        html_path = html_generator.generate_html()

        # Update dashboard index
        MoralFoundationsAnalyzer.update_dashboard_index(output_dir)

        return json_path, csv_path, html_path

    def _generate_summary(self, output_dir: str, timestamp: str):
        """Generate analysis summary"""
        summary_path = os.path.join(output_dir, f"summary_{timestamp}.txt")

        df = pd.DataFrame(self.results)

        with open(summary_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MORAL FOUNDATIONS LLM ANALYSIS SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Responses: {len(self.results)}\n")
            f.write(f"LLMs Tested: {', '.join(df['llm'].unique())}\n")
            f.write(f"Questions Analyzed: {df['question'].nunique()}\n\n")

            # Summary by LLM
            f.write("-" * 80 + "\n")
            f.write("SUM OF SCORES BY LLM AND MORAL FOUNDATION\n")
            f.write("-" * 80 + "\n\n")

            # Filter out failed extractions
            valid_df = df[df['extracted_value'] >= 0]

            for llm in sorted(df['llm'].unique()):
                llm_df = valid_df[valid_df['llm'] == llm]
                f.write(f"\n{llm}:\n")
                f.write(f"  Valid responses: {len(llm_df)}/{len(df[df['llm'] == llm])}\n")

                if len(llm_df) > 0:
                    for foundation in sorted(llm_df['moral_foundation'].unique()):
                        foundation_df = llm_df[llm_df['moral_foundation'] == foundation]
                        sum_score = foundation_df['extracted_value'].sum()
                        f.write(f"  {foundation}: {sum_score}\n")

        print(f"✓ Saved analysis summary to {summary_path}")
        return summary_path

    @staticmethod
    def update_dashboard_index(output_dir: str = "results"):
        """Update index.json with all available reports for dashboard"""
        json_files = glob.glob(os.path.join(output_dir, "moral_foundations_results_*.json"))

        index = []
        for json_file in sorted(json_files, reverse=True):  # Newest first
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                if not data:
                    continue

                # Extract metadata
                llms = sorted(list(set(r['llm'] for r in data)))
                foundations = sorted(list(set(r['moral_foundation'] for r in data)))
                timestamps = [r.get('timestamp') for r in data if r.get('timestamp')]

                # Calculate summary statistics
                valid_responses = [r for r in data if r.get('extracted_value', -1) >= 0]

                # Convert filepath to web-relative path (starting with /)
                relative_path = '/' + json_file.replace('\\', '/')

                index.append({
                    'filename': os.path.basename(json_file),
                    'filepath': relative_path,
                    'timestamp': timestamps[0] if timestamps else None,
                    'llms': llms,
                    'llm_count': len(llms),
                    'foundations': foundations,
                    'question_count': len(set(r['question'] for r in data)),
                    'total_responses': len(data),
                    'valid_responses': len(valid_responses),
                    'date_generated': datetime.fromtimestamp(os.path.getmtime(json_file)).isoformat()
                })
            except Exception as e:
                print(f"Warning: Could not process {json_file}: {e}")
                continue

        # Save index
        index_path = os.path.join(output_dir, 'index.json')
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)

        print(f"✓ Updated dashboard index with {len(index)} reports")
        return index_path


def main():
    """Main execution function"""
    print("=" * 80)
    print("MORAL FOUNDATIONS LLM ANALYZER")
    print("=" * 80)

    # Initialize analyzer
    analyzer = MoralFoundationsAnalyzer()

    # Load questions
    analyzer.load_questions()

    # Option to test with a limited number of questions first
    print("\nOptions:")
    print("1. Analyze all questions (30 questions)")
    print("2. Test with first 5 questions")
    print("3. Test with first 10 questions")

    choice = input("\nEnter choice (1-3, default=1): ").strip() or "1"

    limit_map = {"1": None, "2": 5, "3": 10}
    limit = limit_map.get(choice, None)

    # Run analysis
    analyzer.analyze_all(limit=limit)

    # Save results
    analyzer.save_results()

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
