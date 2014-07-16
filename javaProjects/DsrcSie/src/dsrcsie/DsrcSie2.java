/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package dsrcsie;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.openrdf.model.Statement;
import org.openrdf.repository.Repository;
import org.openrdf.repository.RepositoryConnection;
import org.openrdf.repository.RepositoryException;
import org.openrdf.repository.RepositoryResult;
import org.openrdf.repository.config.RepositoryConfigException;
import org.openrdf.repository.manager.RemoteRepositoryManager;
import org.openrdf.rio.RDFFormat;
import org.openrdf.rio.RDFHandlerException;
import org.openrdf.rio.RDFWriter;
import org.openrdf.rio.Rio;

/**
 *
 * @author Florian
 */
public class DsrcSie2 {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws FileNotFoundException {
        String url = "http://localhost:8080/openrdf-sesame/";
        try {
            RemoteRepositoryManager manager = new RemoteRepositoryManager(url);
            manager.initialize();
            Repository repo = manager.getRepository("1");
            RepositoryConnection con = repo.getConnection();
            Runtime runtime = Runtime.getRuntime();
            int mb = 1024*1024;
            
            String filename = "c:\\Users\\Florian\\Documents\\drugbank.nq";
            int part = 1;
            OutputStreamWriter out = new OutputStreamWriter(new FileOutputStream(filename+"."+part), "UTF-8");
//            RDFWriter writer = Rio.createWriter(RDFFormat.NQUADS, out);
            RDFWriter writer = Rio.createWriter(RDFFormat.NQUADS, out);
            writer.startRDF();
            con.export(writer);
            
//            RepositoryResult<Statement> statements = null;
//            statements = con.getStatements(null, null, null, true);
//            int i = 0;
//            while (statements.hasNext()) {
//                writer.handleStatement(statements.next());
//                i++;
//                if (i == 10) {
//                    int usedMem = (int) ( runtime.totalMemory() - runtime.freeMemory() );
//                    if (usedMem/runtime.totalMemory() >= 0.9) {
//                        writer.endRDF();
//                        out.flush();
//                        part++;
//                        out = new OutputStreamWriter(new FileOutputStream(filename+"."+part), "UTF-8");
//                        writer = Rio.createWriter(RDFFormat.NQUADS, out);
//                        writer.startRDF();
//                    }
//                    
//                }
//            }
//            statements.close();
            writer.endRDF();
            out.flush();
            con.close();
        } catch (RepositoryException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        } catch (RDFHandlerException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        } catch (RepositoryConfigException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

}
