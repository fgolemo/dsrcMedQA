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
import java.util.logging.Level;
import java.util.logging.Logger;
import org.openrdf.model.Statement;
import org.openrdf.repository.Repository;
import org.openrdf.repository.RepositoryConnection;
import org.openrdf.repository.RepositoryException;
import org.openrdf.repository.RepositoryResult;
import org.openrdf.repository.config.RepositoryConfigException;
import org.openrdf.repository.http.HTTPRepository;
import org.openrdf.repository.manager.RemoteRepositoryManager;
import org.openrdf.repository.manager.RepositoryManager;
import org.openrdf.repository.manager.RepositoryProvider;
import org.openrdf.rio.RDFFormat;
import org.openrdf.rio.RDFHandlerException;
import org.openrdf.rio.RDFWriter;
import org.openrdf.rio.Rio;

/**
 *
 * @author Florian
 */
public class DsrcSie {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws FileNotFoundException, RepositoryException {
        String url = "http://localhost:8080/openrdf-sesame/";

        RemoteRepositoryManager manager = new RemoteRepositoryManager(url);
        try {
            manager.initialize();
        } catch (RepositoryException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
        Repository repo = null;
        try {
            repo = manager.getRepository("1");
        } catch (RepositoryConfigException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        } catch (RepositoryException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }

        RepositoryConnection con = null;
        try {
            con = repo.getConnection();
        } catch (RepositoryException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
        Runtime runtime = Runtime.getRuntime();
        int mb = 1024 * 1024;

        String filename = "c:\\Users\\Florian\\Documents\\drugbank.nq";
        int part = 1;
        OutputStream out = new FileOutputStream(filename + "." + part);
        RDFWriter writer = Rio.createWriter(RDFFormat.NQUADS, out);
        try {
            writer.startRDF();
        } catch (RDFHandlerException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
        RepositoryResult<Statement> statements = null;
        try {
            statements = con.getStatements(null, null, null, true);
        } catch (RepositoryException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
        int i = 0;
        while (statements.hasNext()) {
            try {
                writer.handleStatement(statements.next());
            } catch (RDFHandlerException ex) {
                Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
            }
            i++;
            if (i == 10) {
                int usedMem = (int) (runtime.totalMemory() - runtime.freeMemory());
                if (usedMem / runtime.totalMemory() >= 0.9) {
                    try {
                        writer.endRDF();
                    } catch (RDFHandlerException ex) {
                        Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    try {
                        out.flush();
                    } catch (IOException ex) {
                        Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    part++;
                    out = new FileOutputStream(filename + "." + part);
                    writer = Rio.createWriter(RDFFormat.NQUADS, out);
                    try {
                        writer.startRDF();
                    } catch (RDFHandlerException ex) {
                        Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
                    }
                }

            }
        }
        statements.close();
        try {
            writer.endRDF();
        } catch (RDFHandlerException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
        try {
            out.flush();
        } catch (IOException ex) {
            Logger.getLogger(DsrcSie.class.getName()).log(Level.SEVERE, null, ex);
        }
        con.close();
    }

}
