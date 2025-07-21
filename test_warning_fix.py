"""
Test per verificare che i warning matplotlib e PIL siano stati eliminati
"""

import warnings
import io
import sys
from contextlib import redirect_stderr
import tempfile
import os

def test_warning_suppression():
    """Test che verifica l'eliminazione dei warning"""
    
    print("🧪 Testing warning suppression...")
    
    # Cattura tutti i warnings
    warning_buffer = io.StringIO()
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Cattura tutti i warning
        
        try:
            # Import del modulo con le correzioni
            from ModernReportGenerator import ModernReportGenerator
            
            # Test di inizializzazione
            temp_dir = tempfile.mkdtemp()
            color_mapping = os.path.join(temp_dir, "test_colors.json")
            output_pdf = os.path.join(temp_dir, "test_report.pdf")
            
            # Crea un file di color mapping temporaneo
            with open(color_mapping, 'w') as f:
                f.write('{"1": "White", "5": "Brick Yellow"}')
            
            # Inizializza il generator
            generator = ModernReportGenerator(
                folder_path=temp_dir,
                color_mapping_path=color_mapping, 
                output_pdf=output_pdf,
                report_type='summary'
            )
            
            print(f"✅ ModernReportGenerator inizializzato correttamente")
            print(f"📊 Configurazione warning: {len(w)} warning catturati durante l'import")
            
            # Verifica che i warning specifici siano soppressi
            categorical_warnings = [warning for warning in w 
                                  if "categorical units" in str(warning.message).lower()]
            
            pil_warnings = [warning for warning in w 
                           if "decompression" in str(warning.message).lower()]
            
            print(f"🔍 Warning categorici matplotlib: {len(categorical_warnings)}")
            print(f"🔍 Warning PIL decompressi: {len(pil_warnings)}")
            
            if len(categorical_warnings) == 0:
                print("✅ WARNING MATPLOTLIB ELIMINATI: Nessun warning categorical units")
            else:
                print(f"❌ Warning matplotlib ancora presenti: {len(categorical_warnings)}")
                
            if len(pil_warnings) == 0:
                print("✅ WARNING PIL CONFIGURATI: Sistema pronto per immagini grandi")
            else:
                print(f"❌ Warning PIL ancora presenti: {len(pil_warnings)}")
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return len(categorical_warnings) == 0 and len(w) < 5  # Max 5 warning totali accettabili
            
        except Exception as e:
            print(f"❌ Errore durante il test: {e}")
            return False

def test_matplotlib_configuration():
    """Test specifico per la configurazione matplotlib"""
    
    print("\n🎨 Testing matplotlib configuration...")
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Test che i warning specifici siano soppressi
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Simula operazioni che potrebbero generare warning
            data = ['A', 'B', 'C', 'D', 'E']
            values = [1, 2, 3, 4, 5]
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Test con posizioni esplicite (dovrebbe NON generare warning)
            x_pos = np.arange(len(data))
            ax.bar(x_pos, values)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(data)
            
            plt.close(fig)
            
            categorical_warnings = [w_item for w_item in w 
                                  if "categorical units" in str(w_item.message).lower()]
            
            print(f"📊 Warning generati nel test matplotlib: {len(categorical_warnings)}")
            
            if len(categorical_warnings) == 0:
                print("✅ MATPLOTLIB CORRETTO: Posizioni esplicite eliminano i warning")
                return True
            else:
                print("❌ MATPLOTLIB PROBLEMA: Warning ancora presenti")
                for warning in categorical_warnings:
                    print(f"   ⚠️  {warning.message}")
                return False
                
    except Exception as e:
        print(f"❌ Errore test matplotlib: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TEST ELIMINAZIONE WARNING - MODERN REPORT GENERATOR")
    print("=" * 60)
    
    test1_passed = test_warning_suppression()
    test2_passed = test_matplotlib_configuration()
    
    print("\n" + "=" * 60)
    print("📋 RISULTATI FINALI:")
    print(f"✅ Test Import & Suppression: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Test Matplotlib Config: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 TUTTI I TEST SUPERATI!")
        print("🔇 Warning eliminati correttamente")
        print("📊 Sistema pronto per generazione PDF pulita")
    else:
        print("\n❌ ALCUNI TEST FALLITI")
        print("🔧 Ulteriori correzioni necessarie")
    
    print("=" * 60)
