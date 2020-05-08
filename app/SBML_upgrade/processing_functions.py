import glob, requests, subprocess, sys

def create_update_file_from_ressource(path_out, path_to_graph_dir, path_to_docker_yml_file, db_password):
    """
    This function is used to load graph which represent a ressource, with one or several .trig files associated to data graph and one ressource_info_**.ttl file describing the ressource
    """
    with open(path_out + 'update.sh', "w") as update_f:
        update_f.write("delete from DB.DBA.load_list ;\n")
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '*.trig', '');\n")
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', 'ressource_info_*.ttl', 'http://database/ressources');\n")
        update_f.write("rdf_loader_run();\n")
        update_f.write("checkpoint;\n")
        update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
    try:
        dockvirtuoso = subprocess.check_output("docker-compose -f '" + path_to_docker_yml_file + "' ps | grep virtuoso | awk '{print $1}'", shell = True, universal_newlines=True, stderr=subprocess.STDOUT).rstrip()
        subprocess.run("docker exec -t " + dockvirtuoso + " bash -c \'/usr/local/virtuoso-opensource/bin/isql-v 1111 dba \"" + db_password + "\" ./dumps/update.sh'", shell = True, stderr=subprocess.STDOUT)
    except subprocess.SubprocessError as e:
        print("There was an error when trying to load files in virtusoso: " + e)
        sys.exit(3)

def create_update_file_from_graph_dir(path_out, path_to_graph_dir, grah_uri, path_to_docker_yml_file, db_password):
    """
    This function is used to load grpah from a directory, the URI of each graph must be indicated using a <source-file>.<ext>.graph file containing the URI (Cf.http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader)
    """
    with open(path_out + 'update.sh', "w") as update_f:
        update_f.write("delete from DB.DBA.load_list ;\n")
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '*.ttl', '" + grah_uri + "');\n")
        update_f.write("rdf_loader_run();\n")
        update_f.write("checkpoint;\n")
        update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
    try:
        dockvirtuoso = subprocess.check_output("docker-compose -f '" + path_to_docker_yml_file + "' ps | grep virtuoso | awk '{print $1}'", shell = True, universal_newlines=True, stderr=subprocess.STDOUT).rstrip()
        subprocess.run("docker exec -t " + dockvirtuoso + " bash -c \'/usr/local/virtuoso-opensource/bin/isql-v 1111 dba \"" + db_password + "\" ./dumps/update.sh'", shell = True, stderr=subprocess.STDOUT)
    except subprocess.SubprocessError as e:
        print("There was an error when trying to load SBML files in virtusoso: " + e)
        sys.exit(3)

def remove_graph(path_out, uris, path_to_docker_yml_file, db_password):
    with open(path_out + 'remove.sh', "w") as remove_f:
        remove_f.write("log_enable(3,1);\n")
        for uri in uris:
            remove_f.write("SPARQL CLEAR GRAPH  \"" + uri + "\"; \n")
        remove_f.write("delete from DB.DBA.load_list ;\n")
    try:
        dockvirtuoso = subprocess.check_output("docker-compose -f '" + path_to_docker_yml_file + "' ps | grep virtuoso | awk '{print $1}'", shell = True, universal_newlines=True, stderr=subprocess.STDOUT).rstrip()
        subprocess.run("docker exec -t " + dockvirtuoso + " bash -c \'/usr/local/virtuoso-opensource/bin/isql-v 1111 dba \"" + db_password + "\" ./dumps/remove.sh'", shell = True, stderr=subprocess.STDOUT)
    except subprocess.SubprocessError as e:
        print("There was an error when trying to remove graphs: " + e)
        sys.exit(3)


def test_if_graph_exists(url, graph_uri, linked_graph_uri, path_out, path_to_docker_yml_file, db_password):
    """
    This function is used to test if graph exist and to erase it if needed.
    linked_graph_uri MUST be list !
    """
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.text == "true":
        print("SMBL graph " + graph_uri + " and linked graphs " + ",".join(linked_graph_uri) + " already exists.")
        while True:
            t = str(input("Do you want to erase (y/n) :"))
            if t not in ["y", "n"]:
                print("Do you want to erase (y/n) :")
                continue
            else:
                break
        if t == "y":
            l = [graph_uri] + linked_graph_uri
            print(l)
            remove_graph(path_out, l, path_to_docker_yml_file, db_password)
            return True
        else:
            return False
    else:
        return True

def request_annotation(url, g_base_uri, query, sbml_uri, annot_graph_uri, version, header, data):
    data["query"] = query %(g_base_uri, version, sbml_uri, "\n".join(["FROM <" + uri + ">" for uri in annot_graph_uri]))
    print(data["query"])
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        return False
    return True

def ask_for_graph(url, graph_uri):
    """
    This function is used to test if graph a exist without erase
    """
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.text == "true":
        return True
    return False