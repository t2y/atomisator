cd atomisator.filters
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist
cd ..

cd atomisator.readers
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist
cd ..

cd atomisator.enhancers
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist
cd ..

cd atomisator.db
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist
cd ..

cd atomisator.feed
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist    
cd ..

cd atomisator.main
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist    
cd ..

cd atomisator.parser
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist    
cd ..

cd atomisator.outputs
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist    
cd ..


cd atomisator.indexer
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist    
cd ..

cd Atomisator
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist
cd ..

cd pbp.buildbotenv
python setup.py egg_info -RDb "" mregister sdist mupload -r "book"
rm -rf *egg-info build dist    
cd ..

cd pbp.recipe.noserunner
python setup.py egg_info -RDb "" mregister sdist mupload -r "tarek"
rm -rf *egg-info build dist    
cd ..

cd pbp.recipe.trac
python setup.py egg_info -RDb "" mregister sdist mupload -r "tarek"
rm -rf *egg-info build dist    
cd ..

cd pbp.scripts
python setup.py egg_info -RDb "" mregister sdist mupload -r "tarek"
rm -rf *egg-info build dist    
cd ..

cd pbp.skels
python setup.py egg_info -RDb "" mregister sdist mupload -r "tarek"
rm -rf *egg-info build dist    
cd ..


