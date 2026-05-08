"""
Script to search WHO GHO API for disease indicator codes
Helps find API indicators for diseases that don't have data yet
"""
import requests
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

WHO_INDICATOR_API = "https://ghoapi.azureedge.net/api/Indicator"

def search_who_indicators(disease_keywords):
    """
    Search WHO GHO API for indicator codes matching disease keywords
    
    Args:
        disease_keywords: List of keywords to search for (e.g., ["tuberculosis", "TB"])
    """
    print("=" * 70)
    print("SEARCHING WHO GHO API FOR INDICATOR CODES")
    print("=" * 70)
    
    try:
        # Fetch all indicators
        print(f"\nFetching indicator list from WHO GHO API...")
        response = requests.get(WHO_INDICATOR_API, timeout=30)
        response.raise_for_status()
        indicators = response.json().get("value", [])
        
        print(f"✅ Found {len(indicators)} total indicators")
        
        # Search for matching indicators
        matches = []
        for indicator in indicators:
            code = indicator.get("IndicatorCode", "")
            title = indicator.get("IndicatorName", "").lower()
            
            # Check if any keyword matches
            for keyword in disease_keywords:
                if keyword.lower() in title or keyword.lower() in code.lower():
                    matches.append({
                        "code": code,
                        "name": indicator.get("IndicatorName", ""),
                        "language": indicator.get("Language", "")
                    })
                    break
        
        if matches:
            print(f"\n✅ Found {len(matches)} matching indicators:")
            print("-" * 70)
            for match in matches:
                print(f"Code: {match['code']}")
                print(f"Name: {match['name']}")
                print(f"Language: {match['language']}")
                print()
            
            # Test first match for Pakistan
            if matches:
                test_code = matches[0]['code']
                print(f"\n🧪 Testing indicator '{test_code}' for Pakistan...")
                test_url = f"https://ghoapi.azureedge.net/api/{test_code}?$format=json&$filter=SpatialDim eq 'PAK'"
                try:
                    test_response = requests.get(test_url, timeout=30)
                    test_response.raise_for_status()
                    test_data = test_response.json().get("value", [])
                    if test_data:
                        print(f"✅ SUCCESS! Found {len(test_data)} records for Pakistan")
                        print(f"Sample: {test_data[0]}")
                    else:
                        print(f"⚠️  Indicator exists but no data for Pakistan")
                except Exception as e:
                    print(f"❌ Error testing: {str(e)}")
        else:
            print(f"\n⚠️  No matching indicators found for: {', '.join(disease_keywords)}")
            print("Try different keywords or check if disease is tracked by WHO GHO")
        
        return matches
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def main():
    """Main function to search for multiple diseases"""
    
    # Diseases to search for
    diseases_to_search = {
        "tuberculosis": ["tuberculosis", "TB", "tubercul"],
        "hepatitis_a": ["hepatitis a", "hepatitis_a", "hepa"],
        "hepatitis_e": ["hepatitis e", "hepatitis_e", "hepe"],
        "typhoid": ["typhoid", "typh"],
        "meningitis": ["meningitis", "mening"],
        "dengue": ["dengue", "denv"],
        "monkeypox": ["monkeypox", "mpox"],
        "cholera": ["cholera"],  # Already have, but search anyway
        "influenza": ["influenza", "flu"]  # Already have, but search anyway
    }
    
    print("\n" + "=" * 70)
    print("WHO GHO INDICATOR CODE SEARCHER")
    print("=" * 70)
    print("\nThis script will search WHO GHO API for indicator codes")
    print("for diseases that need API data.\n")
    
    all_results = {}
    
    for disease, keywords in diseases_to_search.items():
        print(f"\n{'='*70}")
        print(f"Searching for: {disease.upper()}")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"{'='*70}")
        
        matches = search_who_indicators(keywords)
        all_results[disease] = matches
        
        if matches:
            print(f"\n✅ Found {len(matches)} indicator(s) for {disease}")
        else:
            print(f"\n⚠️  No indicators found for {disease}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    found_diseases = [d for d, m in all_results.items() if m]
    not_found_diseases = [d for d, m in all_results.items() if not m]
    
    if found_diseases:
        print(f"\n✅ Found indicators for: {', '.join(found_diseases)}")
        for disease in found_diseases:
            print(f"\n{disease.upper()}:")
            for match in all_results[disease]:
                print(f"  - {match['code']}: {match['name']}")
    
    if not_found_diseases:
        print(f"\n⚠️  No indicators found for: {', '.join(not_found_diseases)}")
        print("   These diseases may not be tracked by WHO GHO API")
        print("   Try other sources (Pakistan NIH, CDC, etc.)")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Test the found indicator codes for Pakistan data")
    print("2. If data exists, provide codes to integrate into system")
    print("3. If no data, try other sources (see WHERE_TO_FIND_APIS.md)")

if __name__ == "__main__":
    main()



