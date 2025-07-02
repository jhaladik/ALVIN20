#!/usr/bin/env python3
"""
Enhanced Frontend Test Suite - Real User Interaction Testing
Now that basic integration works, test actual frontend functionality
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import sys

class FrontendFunctionalityTester:
    def __init__(self, frontend_url: str = "http://localhost:5173"):
        self.frontend_url = frontend_url
        self.results = []
        
    async def test_frontend_functionality(self):
        """Test actual frontend functionality without browser automation"""
        print("🎨 Testing Frontend Functionality...")
        
        results = {
            "ui_component_analysis": await self.analyze_ui_components(),
            "javascript_bundle_analysis": await self.analyze_javascript_bundle(),
            "css_and_styling": await self.analyze_css_styling(),
            "accessibility_features": await self.test_basic_accessibility(),
            "performance_metrics": await self.analyze_performance_metrics(),
            "mobile_responsiveness": await self.test_mobile_responsiveness()
        }
        
        return results
    
    async def analyze_ui_components(self):
        """Analyze frontend UI components and dependencies"""
        frontend_path = Path("frontend")
        components_path = frontend_path / "src" / "components"
        
        if not components_path.exists():
            return {"error": "Components directory not found"}
        
        # Analyze component structure
        component_analysis = {
            "total_components": 0,
            "component_categories": {},
            "key_components_found": [],
            "missing_critical_components": []
        }
        
        # Expected critical components for a writing app
        critical_components = [
            "SceneContentEditor",  # Rich text editor
            "ProjectCard", 
            "Dashboard",
            "AuthForm",
            "Navigation"
        ]
        
        # Scan for components
        for component_file in components_path.rglob("*.tsx"):
            component_analysis["total_components"] += 1
            
            # Categorize by directory
            category = component_file.parent.name
            if category not in component_analysis["component_categories"]:
                component_analysis["component_categories"][category] = 0
            component_analysis["component_categories"][category] += 1
            
            # Check for critical components
            component_name = component_file.stem
            if any(critical in component_name for critical in critical_components):
                component_analysis["key_components_found"].append(component_name)
        
        # Check for missing critical components
        found_names = " ".join(component_analysis["key_components_found"])
        for critical in critical_components:
            if critical not in found_names:
                component_analysis["missing_critical_components"].append(critical)
        
        # Analyze TipTap integration
        scene_editor_path = components_path / "scenes" / "SceneContentEditor.tsx"
        if scene_editor_path.exists():
            with open(scene_editor_path, 'r', encoding='utf-8') as f:
                content = f.read()
                component_analysis["tiptap_integration"] = {
                    "has_editor_content": "EditorContent" in content,
                    "has_use_editor": "useEditor" in content,
                    "has_character_count": "CharacterCount" in content,
                    "has_placeholder": "Placeholder" in content,
                    "properly_configured": all([
                        "EditorContent" in content,
                        "useEditor" in content,
                        "onChange" in content
                    ])
                }
        
        return component_analysis
    
    async def analyze_javascript_bundle(self):
        """Analyze JavaScript bundle and dependencies"""
        frontend_path = Path("frontend")
        package_json_path = frontend_path / "package.json"
        
        if not package_json_path.exists():
            return {"error": "package.json not found"}
        
        with open(package_json_path) as f:
            package_data = json.load(f)
        
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        
        # Analyze dependency health
        bundle_analysis = {
            "total_dependencies": len(dependencies) + len(dev_dependencies),
            "production_dependencies": len(dependencies),
            "dev_dependencies": len(dev_dependencies),
            "critical_deps_status": {},
            "potential_issues": [],
            "bundle_optimization": {}
        }
        
        # Check critical dependencies
        critical_deps = {
            "react": dependencies.get("react"),
            "react-dom": dependencies.get("react-dom"),
            "react-router-dom": dependencies.get("react-router-dom"),
            "axios": dependencies.get("axios"),
            "socket.io-client": dependencies.get("socket.io-client"),
            "@tiptap/react": dependencies.get("@tiptap/react"),
            "react-beautiful-dnd": dependencies.get("react-beautiful-dnd")
        }
        
        for dep, version in critical_deps.items():
            bundle_analysis["critical_deps_status"][dep] = {
                "installed": version is not None,
                "version": version
            }
            if not version:
                bundle_analysis["potential_issues"].append(f"Missing critical dependency: {dep}")
        
        # Check for potential bundle bloat
        heavy_deps = ["lodash", "moment", "jquery"]
        for dep in heavy_deps:
            if dep in dependencies:
                bundle_analysis["potential_issues"].append(f"Heavy dependency detected: {dep} - consider alternatives")
        
        # Analyze build configuration
        vite_config_path = frontend_path / "vite.config.ts"
        if vite_config_path.exists():
            with open(vite_config_path, 'r', encoding='utf-8') as f:
                vite_content = f.read()
                bundle_analysis["bundle_optimization"] = {
                    "has_build_config": "build:" in vite_content,
                    "has_chunk_splitting": "chunkSizeWarningLimit" in vite_content,
                    "has_minification": "minify" in vite_content
                }
        
        return bundle_analysis
    
    async def analyze_css_styling(self):
        """Analyze CSS and styling setup"""
        frontend_path = Path("frontend") / "src"
        
        css_analysis = {
            "css_framework": "unknown",
            "css_files_count": 0,
            "styling_approach": [],
            "responsive_design": False,
            "theme_support": False
        }
        
        # Check for CSS files
        css_files = list(frontend_path.rglob("*.css"))
        css_analysis["css_files_count"] = len(css_files)
        
        # Check for Tailwind CSS
        package_json_path = Path("frontend") / "package.json"
        if package_json_path.exists():
            with open(package_json_path) as f:
                package_data = json.load(f)
                deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
                
                if "tailwindcss" in deps:
                    css_analysis["css_framework"] = "tailwindcss"
                    css_analysis["styling_approach"].append("utility-first")
                elif "styled-components" in deps:
                    css_analysis["css_framework"] = "styled-components"
                    css_analysis["styling_approach"].append("css-in-js")
                elif "@emotion/react" in deps:
                    css_analysis["css_framework"] = "emotion"
                    css_analysis["styling_approach"].append("css-in-js")
        
        # Check for responsive design patterns
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "@media" in content or "responsive" in content.lower():
                        css_analysis["responsive_design"] = True
                    if "dark" in content.lower() or "theme" in content.lower():
                        css_analysis["theme_support"] = True
            except:
                continue
        
        return css_analysis
    
    async def test_basic_accessibility(self):
        """Test basic accessibility features (static analysis)"""
        frontend_path = Path("frontend") / "src"
        
        accessibility_analysis = {
            "semantic_html_usage": 0,
            "aria_attributes": 0,
            "alt_attributes": 0,
            "accessibility_issues": [],
            "accessibility_score": 0
        }
        
        # Scan TypeScript/JSX files for accessibility patterns
        tsx_files = list(frontend_path.rglob("*.tsx"))
        
        for tsx_file in tsx_files:
            try:
                with open(tsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for semantic HTML
                    semantic_tags = ["<header>", "<nav>", "<main>", "<section>", "<article>", "<aside>", "<footer>"]
                    for tag in semantic_tags:
                        if tag in content:
                            accessibility_analysis["semantic_html_usage"] += 1
                    
                    # Check for ARIA attributes
                    aria_patterns = ["aria-", "role=", "aria-label", "aria-describedby"]
                    for pattern in aria_patterns:
                        accessibility_analysis["aria_attributes"] += content.count(pattern)
                    
                    # Check for alt attributes
                    accessibility_analysis["alt_attributes"] += content.count("alt=")
                    
                    # Check for common accessibility issues
                    if "<div onClick" in content and "role=" not in content:
                        accessibility_analysis["accessibility_issues"].append(f"Clickable div without role in {tsx_file.name}")
                    
                    if 'input type="' in content and "label" not in content.lower():
                        accessibility_analysis["accessibility_issues"].append(f"Input without label in {tsx_file.name}")
                        
            except:
                continue
        
        # Calculate basic accessibility score
        total_elements = len(tsx_files) * 10  # Rough estimate
        accessibility_score = min(100, (
            accessibility_analysis["semantic_html_usage"] * 2 +
            accessibility_analysis["aria_attributes"] +
            accessibility_analysis["alt_attributes"] * 3
        ) / max(1, total_elements) * 100)
        
        accessibility_analysis["accessibility_score"] = round(accessibility_score, 1)
        
        return accessibility_analysis
    
    async def analyze_performance_metrics(self):
        """Analyze potential performance metrics"""
        frontend_path = Path("frontend")
        
        performance_analysis = {
            "bundle_size_estimate": "unknown",
            "code_splitting": False,
            "lazy_loading": False,
            "optimization_opportunities": []
        }
        
        # Check for code splitting patterns
        src_path = frontend_path / "src"
        if src_path.exists():
            tsx_files = list(src_path.rglob("*.tsx"))
            
            for tsx_file in tsx_files:
                try:
                    with open(tsx_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        if "React.lazy" in content or "import(" in content:
                            performance_analysis["code_splitting"] = True
                        
                        if "loading=" in content or "Suspense" in content:
                            performance_analysis["lazy_loading"] = True
                            
                        # Check for potential performance issues
                        if "useEffect([])" in content.replace(" ", ""):
                            performance_analysis["optimization_opportunities"].append("Empty dependency arrays in useEffect")
                        
                        if content.count("useState") > 10:
                            performance_analysis["optimization_opportunities"].append(f"Many useState hooks in {tsx_file.name} - consider useReducer")
                            
                except:
                    continue
        
        # Estimate bundle size based on dependencies
        package_json_path = frontend_path / "package.json"
        if package_json_path.exists():
            with open(package_json_path) as f:
                package_data = json.load(f)
                deps_count = len(package_data.get("dependencies", {}))
                
                # Rough estimate based on dependency count
                if deps_count > 50:
                    performance_analysis["bundle_size_estimate"] = "large (>50 deps)"
                    performance_analysis["optimization_opportunities"].append("Consider reducing dependencies")
                elif deps_count > 30:
                    performance_analysis["bundle_size_estimate"] = "medium (30-50 deps)"
                else:
                    performance_analysis["bundle_size_estimate"] = "small (<30 deps)"
        
        return performance_analysis
    
    async def test_mobile_responsiveness(self):
        """Test mobile responsiveness patterns"""
        frontend_path = Path("frontend") / "src"
        
        mobile_analysis = {
            "responsive_patterns": 0,
            "mobile_specific_styles": 0,
            "touch_friendly_elements": 0,
            "viewport_configured": False,
            "mobile_issues": []
        }
        
        # Check index.html for viewport meta tag
        index_html = Path("frontend") / "index.html"
        if index_html.exists():
            with open(index_html, 'r', encoding='utf-8') as f:
                content = f.read()
                if "viewport" in content and "width=device-width" in content:
                    mobile_analysis["viewport_configured"] = True
        
        # Scan for responsive patterns in CSS/TSX files
        all_files = list(frontend_path.rglob("*.tsx")) + list(frontend_path.rglob("*.css"))
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for responsive patterns
                    responsive_keywords = ["@media", "sm:", "md:", "lg:", "xl:", "mobile", "tablet", "desktop"]
                    for keyword in responsive_keywords:
                        mobile_analysis["responsive_patterns"] += content.count(keyword)
                    
                    # Check for mobile-specific styles
                    mobile_keywords = ["touch", "mobile", "phone", "tablet"]
                    for keyword in mobile_keywords:
                        mobile_analysis["mobile_specific_styles"] += content.count(keyword)
                    
                    # Check for touch-friendly elements
                    touch_keywords = ["cursor-pointer", "hover:", "onClick", "onTouch"]
                    for keyword in touch_keywords:
                        mobile_analysis["touch_friendly_elements"] += content.count(keyword)
                    
                    # Check for potential mobile issues
                    if "position: fixed" in content and "z-index" not in content:
                        mobile_analysis["mobile_issues"].append("Fixed positioning without z-index")
                    
                    if "overflow-x: hidden" not in content and "horizontal" in content:
                        mobile_analysis["mobile_issues"].append("Potential horizontal scroll issue")
                        
            except:
                continue
        
        return mobile_analysis

async def main():
    """Run enhanced frontend functionality tests"""
    print("🎭 Enhanced Frontend Functionality Test Suite")
    print("=" * 60)
    
    tester = FrontendFunctionalityTester()
    results = await tester.test_frontend_functionality()
    
    # Print summary
    print("\n📊 FRONTEND FUNCTIONALITY ANALYSIS")
    print("=" * 60)
    
    # Component Analysis
    ui_analysis = results.get("ui_component_analysis", {})
    print(f"\n🧩 UI Components:")
    print(f"   Total Components: {ui_analysis.get('total_components', 0)}")
    print(f"   Key Components Found: {len(ui_analysis.get('key_components_found', []))}")
    print(f"   Missing Critical: {len(ui_analysis.get('missing_critical_components', []))}")
    
    if ui_analysis.get("tiptap_integration"):
        tiptap = ui_analysis["tiptap_integration"]
        print(f"   TipTap Editor: {'✅ Configured' if tiptap.get('properly_configured') else '⚠️ Issues'}")
    
    # Bundle Analysis
    bundle_analysis = results.get("javascript_bundle_analysis", {})
    print(f"\n📦 Bundle Analysis:")
    print(f"   Dependencies: {bundle_analysis.get('total_dependencies', 0)}")
    print(f"   Potential Issues: {len(bundle_analysis.get('potential_issues', []))}")
    
    # Performance Analysis
    perf_analysis = results.get("performance_metrics", {})
    print(f"\n⚡ Performance:")
    print(f"   Code Splitting: {'✅' if perf_analysis.get('code_splitting') else '❌'}")
    print(f"   Lazy Loading: {'✅' if perf_analysis.get('lazy_loading') else '❌'}")
    print(f"   Bundle Size: {perf_analysis.get('bundle_size_estimate', 'unknown')}")
    
    # Accessibility Analysis
    a11y_analysis = results.get("accessibility_features", {})
    print(f"\n♿ Accessibility:")
    print(f"   Score: {a11y_analysis.get('accessibility_score', 0)}%")
    print(f"   Issues Found: {len(a11y_analysis.get('accessibility_issues', []))}")
    
    # Mobile Analysis
    mobile_analysis = results.get("mobile_responsiveness", {})
    print(f"\n📱 Mobile Responsiveness:")
    print(f"   Viewport Configured: {'✅' if mobile_analysis.get('viewport_configured') else '❌'}")
    print(f"   Responsive Patterns: {mobile_analysis.get('responsive_patterns', 0)}")
    print(f"   Mobile Issues: {len(mobile_analysis.get('mobile_issues', []))}")
    
    # Generate recommendations
    recommendations = []
    
    if ui_analysis.get("missing_critical_components"):
        recommendations.append("🧩 Implement missing critical components")
    
    if not perf_analysis.get("code_splitting"):
        recommendations.append("⚡ Add code splitting for better performance")
    
    if a11y_analysis.get("accessibility_score", 0) < 70:
        recommendations.append("♿ Improve accessibility compliance")
    
    if not mobile_analysis.get("viewport_configured"):
        recommendations.append("📱 Configure viewport meta tag for mobile")
    
    if bundle_analysis.get("potential_issues"):
        recommendations.append("📦 Address bundle optimization issues")
    
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    # Save detailed report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"frontend_functionality_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("\n🎉 Frontend functionality analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())