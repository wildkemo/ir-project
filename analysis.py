import json
from collections import Counter

def create_bar_chart(data, max_width=30):
    if not data:
        return '  (No data available)'
    max_val = max((d[1] for d in data))
    chart = ''
    for label, value in data:
        bar_length = int(value / max_val * max_width)
        bar = '█' * bar_length
        chart += f'  {label:<12} | {bar} {value}\n'
    return chart

def run_analysis():
    try:
        with open('processed.json', 'r') as f:
            data = json.load(f)
        if not data:
            print('Error: processed.json is empty.')
            return
        total_records = len(data)
        all_tokens = []
        token_lengths = []
        for item in data:
            tokens = item.get('tokens', [])
            all_tokens.extend(tokens)
            token_lengths.append(len(tokens))
        avg_tokens = sum(token_lengths) / total_records if total_records > 0 else 0
        unique_tokens = len(set(all_tokens))
        vocab_richness = unique_tokens / len(all_tokens) * 100 if all_tokens else 0
        counts = Counter(all_tokens)
        track_languages = {'python', 'javascript', 'typescript', 'go', 'rust', 'java', 'cpp', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin', 'sql', 'shell', 'bash', 'perl', 'scala', 'dart', 'lua', 'html', 'css', 'react', 'node', 'vue', 'angular'}
        lang_counts = Counter({k: v for k, v in counts.items() if k in track_languages})
        general_counts = Counter({k: v for k, v in counts.items() if k not in track_languages})
        print('\n' + '=' * 50)
        print('      🚀 WEB INTELLIGENCE ANALYSIS DASHBOARD')
        print('=' * 50)
        print('\n[📊 DATASET SUMMARY]')
        print(f'  • Total Repositories Scanned : {total_records}')
        print(f'  • Total Keywords Extracted    : {len(all_tokens)}')
        print(f'  • Unique Vocabulary Size     : {unique_tokens}')
        print(f'  • Avg. Keywords per Repo     : {avg_tokens:.1f}')
        print(f'  • Vocabulary Richness        : {vocab_richness:.1f}%')
        print('\n[💻 TOP PROGRAMMING LANGUAGES & TECH]')
        print(create_bar_chart(lang_counts.most_common(8)))
        print('\n[🔍 TOP GENERAL TECH KEYWORDS]')
        common_general = general_counts.most_common(10)
        for i, (word, count) in enumerate(common_general, 1):
            print(f'  {i}. {word:<12} ({count} occurrences)')
        print('\n[🌐 SOURCE DISTRIBUTION]')
        domains = [item.get('url', '').split('/')[2] for item in data if 'url' in item]
        domain_counts = Counter(domains)
        for domain, count in domain_counts.most_common(3):
            print(f'  • {domain:<15}: {count} records')
        print('\n' + '=' * 50)
        print('      Analysis Complete. Data is ready for IR.')
        print('=' * 50 + '\n')
    except FileNotFoundError:
        print('Error: processed.json not found. Please run process.py first.')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
if __name__ == '__main__':
    run_analysis()
